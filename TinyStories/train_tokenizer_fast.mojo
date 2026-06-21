from std.collections import Optional
from std.memory import UnsafePointer
import std.os as os
from std.pathlib import Path
from std.time import perf_counter
from std.python import Python

from static_indexed_list import StaticIndexedList

comptime NULL = "\x00"
comptime TINY_STORIES = "karpathy/tinystories-gpt4-clean"

comptime Token = UInt16
comptime Digram = Tuple[Token, Token]
comptime DigramIndices = Dict[Digram, List[Int]]
comptime MergeRule = Tuple[Token, Digram]


# Could abstract the argument into Iterable[Token]
def build_digram_indices(tokens: StaticIndexedList[Token]) -> DigramIndices:
    var indices = DigramIndices()
    var first_token = tokens[0]
    var second_token: Token
    for i in range(1, len(tokens)):
        second_token = tokens[i]
        var digram = (first_token, second_token)
        if digram not in indices:
            indices[digram] = []
        try:
            indices[digram].append(i - 1)
        except KeyError:
            assert False  # unreachable
        first_token = second_token
    return indices^


def remove[T: Equatable & Copyable](mut list: List[T], value: T):
    for i in range(len(list)):
        if list[i] == value:
            _ = list.pop(i)
            return

def merge_tokens(
    mut tokens: StaticIndexedList[Token],
    mut digram_indices: DigramIndices,
    merge_rule: MergeRule,
):
    var token = merge_rule[0]
    var digram = merge_rule[1]
    var new_digram : Digram
    try:
        while digram_indices[digram]:
            print("1.", digram, digram_indices[digram])
            var index = digram_indices[digram].pop(0)
            print("2.", index)
            # Update the digram locations
            var prev_index = tokens.prev[index]
            print("-")
            if prev_index >= tokens.head:
                var prev_token = tokens[prev_index]
                remove(
                    digram_indices[(prev_token, digram[0])],
                    prev_index,
                )
                new_digram = (prev_token, token)
                if new_digram not in digram_indices:
                    digram_indices[new_digram] = []
                digram_indices[new_digram].append(prev_index)
            
            print("--")

            var next_index = tokens.next[index]
            if next_index <= tokens.tail:
                var next_next_index = tokens.next[index]
                var next_next_token = tokens[next_next_index]
                print("reachable")
                print(digram_indices, (digram[1], next_next_token)) # digram not found
                _ = digram_indices[(digram[1], next_next_token)].copy()
                print("unreachable")
                remove(
                    digram_indices[(digram[1], next_next_token)],
                    next_index,
                ) # issue here?
                
                new_digram = (token, next_next_token)
                if new_digram not in digram_indices:
                    digram_indices[new_digram] = []
                digram_indices[new_digram].append(index)
        
            print("---") # We never reach this point.

            # Update the token and remove the next one
            tokens[index] = token
            _ = tokens.pop(next_index)
            print("3.", tokens)
    except KeyError:
        assert False


def display_merge_rules(merge_rules: List[MergeRule]):
    var token_to_string: Dict[Token, String] = {}
    for token in range(Token(256)):
        token_to_string[token] = chr(Int(token))
    for rule in merge_rules:
        var token = rule[0]
        var digram = rule[1]
        try:
            token_to_string[token] = (
                token_to_string[digram[0]] + token_to_string[digram[1]]
            )
        except KeyError:
            assert False
    for merge_rule in merge_rules:
        var token = merge_rule[0]
        var digram = merge_rule[1]
        try:
            print(
                repr(token_to_string[token]),
                "=",
                repr(token_to_string[digram[0]]),
                "+",
                repr(token_to_string[digram[1]]),
            )
        except KeyError:
            assert False


def train(
    vocab_size: Token,
    n: Optional[Int] = None,  # number of bytes to read from the corpus
) raises:
    var ds = Python.import_module("datasets")  # from huggingface
    var merge_rules: List[MergeRule] = []
    var tokens: StaticIndexedList[Token] = []
    var prev: List[Int] = []
    var next: List[Int] = []

    # Load the corpus
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
        var size = os.stat("corpus.bin").st_size
        print("Full corpus: {} GB".format(round(Float64(size) / 1000**3, 2)))
        corpus = file.read(n.or_else(size))
        print(
            "Corpus fragment loaded: {} MB".format(
                round(Float64(corpus.byte_length()) / 1000**2, 2)
            )
        )
    
    tokens = StaticIndexedList[Token]([Token(byte) for byte in corpus.as_bytes()])

    print(perf_counter() - t0, "seconds")
    print()

    var digram_indices = build_digram_indices(tokens)

    # Find the most frequent digram, merge the tokens, update the merge rules
    t0 = perf_counter()
    for next_token in range(Token(256), vocab_size):
        var top_digram: Digram = (0, 0)
        var top_count: UInt32 = 0
        for entry in digram_count.items():
            if entry.value > top_count:
                top_count = entry.value
                top_digram = entry.key
        merge_rule = (next_token, top_digram)
        tokens = merge_tokens(tokens, prev, next, digram_count, merge_rule)
        merge_rules.append(merge_rule)
    # TODO: display the merge rules in a nice format (with the actual characters, not the token ids)
    t1 = perf_counter() - t0
    # print(merge_rules)
    print(t1, "seconds")

    print()
    display_merge_rules(merge_rules)


def main() raises:
    train(vocab_size=256 + 100, n=1_000_000)
