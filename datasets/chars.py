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


def build_dictionary(root_dir):
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
def count_digrams(tokens: NDArray[np.uint16]) -> dict[tuple[np.uint16, np.uint16], int]:
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

# Optimization:
def count_digrams_(tokens: dict[str, NDArray[np.uint16]]) -> dict[tuple[np.uint16, np.uint16], int]:
    # Pack all consecutive pairs into a single (N, 2) array
    pairs = np.concatenate([
        np.stack([array[:-1], array[1:]], axis=1)
        for array in tokens.values()
        if len(array) > 1
    ])
    
    # Encode each pair as a single uint32 for fast counting
    keys = pairs[:, 0].astype(np.uint32) << 16 | pairs[:, 1].astype(np.uint32)
    unique, counts = np.unique(keys, return_counts=True)
    
    # Decode back to pairs and sort by frequency
    digrams = {
        (int(k >> 16), int(k & 0xFFFF)): int(c)
        for k, c in sorted(zip(unique, counts), key=lambda x: x[1], reverse=True)
    }
    return digrams

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

    d = build_dictionary("dump")
    print("len(d):", len(d))
    # print a small, "random" subset of the dictionary
    for i, (k, v) in enumerate(d.items()):
        if i >= 10:
            break
        print(f"{k}: {v[:10]}... (length: {len(v)})")

    digs = count_digrams(d)
    for k, v in list(digs.items())[:100]:
        # decode the digram back to characters
        chars = "".join(chr(x) for x in k)
        print(f"{chars}: {v}")
