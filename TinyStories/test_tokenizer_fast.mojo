from std.testing import assert_equal, assert_true, assert_raises, TestSuite

from static_indexed_list import StaticIndexedList, StaticIndexedListIter
from train_tokenizer_fast import (
    Digram,
    DigramIndices,
    Token,
    build_digram_indices,
    merge_tokens,
)


def test_build_digram_indices() raises:
    var tokens = StaticIndexedList[Token]([0, 1, 2, 3, 4, 0, 1, 2, 3, 4])
    var expected: DigramIndices = {
        Digram(0, 1): [0, 5],
        Digram(1, 2): [1, 6],
        Digram(2, 3): [2, 7],
        Digram(3, 4): [3, 8],
        Digram(4, 0): [4],
    }

    assert_equal(build_digram_indices(tokens), expected)

def test_merge_digrams() raises:
    var tokens = StaticIndexedList[Token]([0, 1, 2, 3, 4, 0, 1, 2, 3, 4])
    var digram_indices = build_digram_indices(tokens)

    var merge_rule = (Token(5), Digram(0, 1))
    merge_tokens(tokens, digram_indices, merge_rule)
    #print(tokens)
    #print(digram_indices) 
    expected_tokens = StaticIndexedList[Token]([5, 2, 3, 4, 5, 2, 3, 4])
    expected_digram_indices: DigramIndices = {
        Digram(5, 2): [0, 4],
        Digram(2, 3): [1, 5],
        Digram(3, 4): [2, 6],
        Digram(4, 5): [3],
    }
    #assert_equal(tokens, expected_tokens)
    #assert_equal(digram_indices, expected_digram_indices)

def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
