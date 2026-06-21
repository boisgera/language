from std.testing import assert_equal, assert_true, assert_raises, TestSuite

from static_indexed_list import StaticIndexedList, StaticIndexedListIter

def test_init() raises:
    var sll = StaticIndexedList([4, 2, 1])
    assert_equal(List(sll), [4, 2, 1])

def test_iter() raises:
    var sll = StaticIndexedList([4, 2, 1])
    for i in range(len(sll)):
        assert_equal(sll[i], [4, 2, 1][i])

def test_remove() raises:
    var sll = StaticIndexedList([4, 2, 1])
    sll.remove(1)
    assert_equal(List(sll), [4, 1])
    sll.remove(2)
    assert_equal(List(sll), [4])
    sll.remove(0)
    assert_equal(List(sll), [])

def test_equal() raises:
    var sll1 = StaticIndexedList([4, 2, 1])
    var sll2 = StaticIndexedList([4, 2, 1])
    var sll3 = StaticIndexedList([4, 2])
    assert_true(sll1 == sll2)
    assert_true(sll1 != sll3)
    sll2.remove(2)
    print(sll2)
    assert_true(sll1 != sll2)
    assert_true(sll2 == sll3)

def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()