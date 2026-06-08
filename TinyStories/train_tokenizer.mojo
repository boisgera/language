from std.pathlib import Path
from std.time import perf_counter
from std.python import Python

comptime NULL = "\x00"
comptime TINY_STORIES = "karpathy/tinystories-gpt4-clean"

comptime Digram = Tuple[UInt16, UInt16]
comptime DigramCount = Dict[Digram, UInt32]

def digram_frequencies(corpus: String) -> DigramCount:
    var count = DigramCount()
    for i in range(corpus.byte_length() - 2):
        var digram = (UInt16(corpus.as_bytes()[i]), UInt16(corpus.as_bytes()[i + 1]))
        count[digram] = count.get(digram, 0) + 1
    return count^

def cmp_fn(a: Tuple[Digram, UInt32], b: Tuple[Digram, UInt32]) capturing -> Bool:
    return a[1] > b[1]

def main() raises:
    var warnings = Python.import_module("warnings")
    warnings.filterwarnings("ignore")

    var ds = Python.import_module("datasets")
    var ps = Python.import_module("pandas")
    var torch = Python.import_module("torch")
    var tqdm = Python.import_module("tqdm")

    var t0 : Float64

    if not Path("corpus.bin").exists():
        var hg_dataset = ds.load_dataset(TINY_STORIES)
        var dataset = hg_dataset["train"]["text"]
        print("Dataset loaded. Number of samples:", len(dataset))

        var t0 = perf_counter()
        var file = open("corpus.bin", "w") 
        for text in dataset: 
            file.write(NULL + String(text))
        file.write("NULL")
        print(perf_counter() - t0, "seconds")

    var t0 = perf_counter()
    file = open("corpus.bin", "r")
    var corpus = file.read()
    print("Corpus loaded. Length:", corpus.byte_length())
    print(perf_counter() - t0, "seconds")
    

    t0 = perf_counter()
    var digram_count = digram_frequencies(corpus)
    var items = List[Tuple[Tuple[UInt16, UInt16], UInt32]]()
    for entry in digram_count.items():
        items.append((entry.key, entry.value))

    sort[cmp_fn=cmp_fn](items)
    print("Top 10 digrams:")
    for i in range(10):
        var digram = items[i][0]
        var count = items[i][1]
        print(String.format("{0}: {1}", digram, count))
    print(perf_counter() - t0, "seconds")