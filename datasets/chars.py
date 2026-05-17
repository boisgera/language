import os
import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
import tqdm


def collect_characters(root_dir):
    chars = set()

    txt_files = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(root_dir)
        for filename in filenames
        if filename.lower().endswith(".txt")
    ]
    num_files = len(txt_files)
    print(f"Found {num_files} files in {root_dir}")

    for file_path in tqdm.tqdm(
        txt_files,
        total=num_files,
        desc="Collecting characters",
    ):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                chars.update(f.read())
        except (UnicodeDecodeError, OSError) as e:
            print(f"Skipping {file_path}: {e}")

    l = list(chars)
    l.sort()
    return l


def build_corpus(root_dir):
    root_dir = Path(root_dir)
    txt_files = [
        path
        for path in root_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".txt"
    ]
    num_files = len(txt_files)
    print(f"Found {num_files} files in {root_dir}")

    d = {}

    for file_path in tqdm.tqdm(
        txt_files,
        total=num_files,
        desc="Collecting characters",
    ):
        raw_data = file_path.read_bytes()
        array = np.frombuffer(raw_data, dtype=np.uint8).astype(np.uint16)
        d[file_path.stem] = array

    s = sys.getsizeof(d)
    s += sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in d.items())
    print(f"Dictionary size: {s / (1024**3):.2f} GB")
    return d


# Bytes never found in valid UTF-8 sequences:
# 0xC0, 0xC1, 0xFE, 0xFF


# TODO:
# - add a special token for start / end of a file
# - merge all arrays into a giant array, with a separator token between files?
#   Afterwards, one can split this giant array into smaller arrays at will.
def count_digrams(tokens):
    digrams = {}
    for array in tqdm.tqdm(tokens.values()):
        for i in range(len(array) - 1):
            t = tuple(array[i : i + 2])
            digrams[t] = digrams.get(t, 0) + 1
    # sort the dictionary by frequency, in descending order
    digrams = dict(
        sorted(
            digrams.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    return digrams


# Optimization: Use numpy to count digrams more efficiently.
def count_digrams_perf(
    corpus: dict[str, NDArray[np.uint16]],
) -> list[tuple[tuple[np.uint16, np.uint16], int]]:
    # Pack all consecutive pairs into a single (N, 2) array
    pairs = np.concatenate(
        [
            np.stack([array[:-1], array[1:]], axis=1)
            for array in corpus.values()
            if len(array) > 1
        ]
    )

    # Encode each pair as a single uint32 for fast counting
    keys = pairs[:, 0].astype(np.uint32) << 16 | pairs[:, 1].astype(np.uint32)
    unique, counts = np.unique(keys, return_counts=True)

    # Decode back to pairs and sort by frequency
    digrams = [
        ((int(k >> 16), int(k & 0xFFFF)), int(c))
        for k, c in sorted(zip(unique, counts), key=lambda x: x[1], reverse=True)
    ]
    return digrams

# TODO:
# - use the top digram to create a new token, and replace all occurrences of 
#   that digram with the new token in the data. The issue is that we will have
#   to create a new array for that...

def replace(digram, digram_token, corpus):
    # mutates the corpus in-place, replacing all occurrences of the digram 
    # with the new token
    for key, data in corpus.items():
        new_data = []
        i = 0
        while i < len(data) - 1:
            if (data[i], data[i + 1]) == digram:
                new_data.append(digram_token)
                i += 2  # skip the next token as well
            else:
                new_data.append(data[i])
                i += 1
        new_data.append(data[-1])  # add the last token, which is not part of any digram
        corpus[key] = np.array(new_data, dtype=np.uint16)

# This stuff should be refactored and called what it is: tokenizer "1 step" or 
# similar. That's it.
# Also adapt the token "dictionary" to be simply an ordered list of
# (token, token) -> token merge sequences.
def replace_perf(digram, digram_token, corpus):
    a, b = digram
    for key, data in corpus.items():
        if len(data) < 2:
            continue
        # find positions where the digram starts
        mask = (data[:-1] == a) & (data[1:] == b)
        
        # remove positions that overlap with a previous match 
        # (e.g. [x, x, x] with digram (x,x))
        match_idx = np.nonzero(mask)[0]
        # eliminate overlapping matches (e.g. [x, x, x] with digram (x,x))
        if len(match_idx) > 0:
            keep = np.diff(match_idx, prepend=-2) >= 2
            match_idx = match_idx[keep]
        if len(match_idx) == 0:
            continue

        data[match_idx] = digram_token
        drop = match_idx + 1
        keep_mask = np.ones(len(data), dtype=bool)
        keep_mask[drop] = False
        corpus[key] = data[keep_mask]

if __name__ == "__main__":
    # chars = collect_characters("dump")
    # print("len(chars):", len(chars))
    # print("max(ord(c) for c in chars):", max(ord(c) for c in chars))
    # #print([ord(c) for c in chars])
    # print("code points above 2^16:")
    # # count how many characters have code points above 2^16
    # print(sum(1 for c in chars if ord(c) >= 2**16))
    # #print("".join([c for c in chars if ord(c) >= 2**16]))
    # print("code points above 255:")
    # # count how many characters have code points above 255
    # print("Characters out of the BMP:")
    # print(sum(1 for c in chars if ord(c) >= 256))
    # print("".join([c for c in chars if ord(c) >= 256]))
    # print("".join(chars))

    print()

    corpus = build_corpus("dump")
    print("len(corpus):", len(corpus))
    # print a small subset of the dictionary
    # for i, (k, v) in enumerate(corpus.items()):
    #     if i >= 10:
    #         break
    #     print(f"{k}: {v[:10]}... (length: {len(v)})")

    # Token "dictionary": index (token) -> byte (~ string)
    token_to_bytes = [bytes([i]) for i in range(256)]
    # Question: do I need to keep track of the (token, token) -> token map too?
    # (to reimplement a tokenizer, probably yes)

    for i in range(10):
        digram_counts = count_digrams_perf(corpus)
        new_digram, count = digram_counts[0]
        print(f"Top digram: {bytes(new_digram)}: {count} count")
        
        # Update the token dictionary
        new_token = len(token_to_bytes)
        new_bytes = token_to_bytes[new_digram[0]] + token_to_bytes[new_digram[1]]
        token_to_bytes.append(new_bytes)
        print(f"New token: {new_token}: {new_bytes}")

        # Substitute the new token for the digram in the corpus        
        replace_perf(new_digram, new_token, corpus)

    # TODO: save the token dictionnary somehow.
