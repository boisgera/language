from std.testing import assert_equal, assert_true, assert_raises, TestSuite

from static_indexed_list import StaticLinkedList, StaticLinkedListIter

def test_init() raises:
    var sll = StaticLinkedList([4, 2, 1])
    assert_equal(List(sll), [4, 2, 1])

def test_iter() raises:
    var sll = StaticLinkedList([4, 2, 1])
    for i in range(len(sll)):
        assert_equal(sll[i], [4, 2, 1][i])

def test_remove() raises:
    var sll = StaticLinkedList([4, 2, 1])
    sll.remove(1)
    assert_equal(List(sll), [4, 1])
    sll.remove(2)
    assert_equal(List(sll), [4])
    sll.remove(0)
    assert_equal(List(sll), [])

def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()