from std.collections import Optional
from std.memory import UnsafePointer
import std.os as os
from std.pathlib import Path
from std.time import perf_counter
from std.python import Python

comptime NULL = "\x00"
comptime TINY_STORIES = "karpathy/tinystories-gpt4-clean"

comptime Token = UInt16
comptime Digram = Tuple[Token, Token]
comptime DigramLocations = Dict[Digram, List[Int]]
comptime MergeRule = Tuple[Token, Digram]


def build_digram_locations(tokens: List[Token]) -> DigramLocations:
    var locations = DigramLocations()
    var first_token = tokens[0]
    var second_token: Token
    for i in range(1, len(tokens)):
        second_token = tokens[i]
        var digram = (first_token, second_token)
        if digram not in locations:
            locations[digram] = []
        try:
            locations[digram].append(i - 1)
        except KeyError:
            assert False # unreachable
        first_token = second_token
    return locations^

def remove[T: Equatable & Copyable](mut list: List[T], value: T):
    for i in range(len(list)):
        if list[i] == value:
            _ = list.pop(i)
            return

struct StaticLinkedListIter[
    T: Copyable & Movable, origin: Origin
](Copyable & Movable):
    var plist: Pointer[StaticLinkedList[Self.T], Self.origin]
    var current: Int

    def __init__(out self, ref [Self.origin] list: StaticLinkedList[Self.T]):
        self.plist = Pointer(to=list)
        self.current = self.plist[].head

    def __iter__(self) -> ref[self] Self:
        return self

    def __next__(mut self) -> ref[self.plist[].list] Self.T:
        ref list = self.plist[]
        ref value = list[self.current]
        self.current = list.next[self.current]
        return value

    def __has_next__(self) -> Bool:
        return self.current != StaticLinkedList[Self.T].NO_NEXT


struct StaticLinkedList[T: Copyable & Movable](Copyable & Movable, Sized):
    var list: List[Self.T]
    var prev: List[Int]
    var next: List[Int]
    # var free: List[Bool]     # TODO: maintain a free list?
    var head: Int
    var tail: Int


    comptime NO_PREV = -1
    comptime NO_NEXT = -1
    comptime NO_HEAD = -1
    comptime NO_TAIL = -1

    def __init__(out self, var list: List[Self.T]):
        self.list = list^
        self.prev   = []
        self.next   = []
        #self.free   = []
        for i in range(len(self.list)):
            self.prev.append(i - 1) # -1 when i = 0 
            self.next.append(i + 1)
            # self.free.append(False)
        if self.list:
            self.prev[0] = Self.NO_PREV
            self.next[len(self.next) - 1] = Self.NO_NEXT
            self.head = 0
            self.tail = len(self.list) - 1
        else:
            self.head = Self.NO_HEAD
            self.tail = Self.NO_TAIL

    def __getitem__(ref self, index: Int) -> ref[self.list] Self.T:
        return self.list[index]

    def __setitem__(mut self, index: Int, var value: Self.T):
        self.list[index] = value^
    
    def remove(mut self, index: Int):
        var p = self.prev[index]
        var n = self.next[index]
        if p != Self.NO_PREV:
            self.next[p] = n
        else:
            self.head = n
        if n != Self.NO_NEXT:
            self.prev[n] = p
        else:
            self.tail = p

    def __iter__[origin: Origin](ref [origin] self) -> StaticLinkedListIter[Self.T, origin]:
        return StaticLinkedListIter[Self.T, origin](self)

    def __len__(self) -> Int:
        if self.head == Self.NO_HEAD:
            return 0
        var count = 1
        var i = self.next[self.head]
        while i != Self.NO_NEXT:
            count += 1
            i = self.next[i]
        return count

# TODO: review this in detail.
# Open question: replace the tokens/prev/next by a dedicated structure that
# abstracts the machinery?
def merge_tokens(
    mut tokens: List[Token],
    mut prev: List[Int],
    mut next: List[Int],
    mut digram_locations: DigramLocations,
    merge_rule: MergeRule,
):
    var token = merge_rule[0]
    var digram = merge_rule[1]
    try: 
        while digram_locations[digram]:
            index = digram_locations[digram][0]
            # Update the token
            tokens[index] = token
            # Rewire: skip the next token
            var next_index = next[index]
            var next_next_index = next[next_index]
            next[index] = next_next_index
            if next_next_index != -1:
                prev[next_next_index] = index
            # Update the digram locations
            remove(digram_locations[digram], index)
            var prev_index = prev[index]
            if prev_index != -1:
                remove(digram_locations[(tokens[prev_index], digram[0])], prev_index)
                digram_locations[(token, tokens[next_next_index])].append(prev_index)
            if next_next_index != -1:
                remove(digram_locations[(digram[1], tokens[next_next_index])], next_index)
                digram_locations[(token, tokens[next_next_index])].append(index)
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
    var tokens: List[Token] = []
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
    for i, byte in enumerate(corpus.as_bytes()):
        tokens.append(Token(byte))
        prev.append(i - 1)  # -1 when no prev token.
        next.append(i + 1)
    next[len(next) - 1] = -1  # for the last token
    print(perf_counter() - t0, "seconds")
    print()

    var digram_locations = build_digram_locations(tokens)

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
