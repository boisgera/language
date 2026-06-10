import std.os as os
from std.pathlib import Path
from std.time import perf_counter
from std.python import Python

comptime N = 1_000_000 # number of bytes to read from the corpus
comptime NULL = "\x00"
comptime TINY_STORIES = "karpathy/tinystories-gpt4-clean"

comptime Token = UInt16
comptime Digram = Tuple[Token, Token]
comptime DigramCount = Dict[Digram, UInt32]
comptime MergeRule = Tuple[Digram, Token]

def digram_frequencies(corpus: String) -> DigramCount:
    var count = DigramCount()
    var corpus_bytes = corpus.as_bytes()
    var first_token = Token(corpus_bytes[0])
    var second_token : Token
    for i in range(1, len(corpus_bytes)):
        second_token = Token(corpus_bytes[i])
        var digram = (first_token, second_token)
        count[digram] = count.get(digram, 0) + 1
        first_token = second_token
    return count^

def main() raises:
    var ds = Python.import_module("datasets") # from huggingface
    var t0 : Float64

    if not Path("corpus.bin").exists():
        var hg_dataset = ds.load_dataset(TINY_STORIES)
        var dataset = hg_dataset["train"]["text"]
        print("Dataset loaded. Number of samples:", len(dataset))

        t0 = perf_counter()
        with open("corpus.bin", "w") as file:
            for text in dataset: 
                file.write(NULL + String(text))
            file.write("NULL")
        print(perf_counter() - t0, "seconds")
        print()

    t0 = perf_counter()
    with open("corpus.bin", "r") as file:
        print("Full corpus: {} GB".format(
            round(Float64(os.stat("corpus.bin").st_size) / 1000**3, 2)
        ))
        corpus = file.read(N)
        print("Corpus fragment loaded: {} MB".format(
            round(Float64(corpus.byte_length()) / 1000**2, 2)
        ))
    print(perf_counter() - t0, "seconds")
    print()
    
    t0 = perf_counter()
    var digram_count = digram_frequencies(corpus)
    var items = List[Tuple[Digram, UInt32]]()
    for entry in digram_count.items():
        items.append((entry.key, entry.value))

    # TODO: replace the sort by a mere "find max".
    # TODO: iterate and store the merge rules
    # TODO: display the merge rules in a nice format (with the actual characters, not the token ids)

    def cmp_fn(a: Tuple[Digram, UInt32], b: Tuple[Digram, UInt32]) capturing -> Bool:
        return a[1] > b[1]
    sort[cmp_fn=cmp_fn](items)
    print("Top 10 digrams:")
    for i in range(10):
        var digram = items[i][0]
        var count = items[i][1]
        print(String.format("{0}: {1}", digram, count))
    print(perf_counter() - t0, "seconds")