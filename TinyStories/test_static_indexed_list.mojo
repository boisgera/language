from std.testing import assert_equal, assert_true, assert_raises, TestSuite

from static_indexed_list import StaticIndexedList, StaticIndexedListIter

def test_init() raises:
    var items = StaticIndexedList([4, 2, 1])
    assert_equal(List(items), [4, 2, 1])

def test_iter() raises:
    var items = StaticIndexedList([4, 2, 1])
    for i in range(len(items)):
        assert_equal(items[i], [4, 2, 1][i])

def test_remove() raises:
    var items = StaticIndexedList([4, 2, 1])
    _ = items.pop(1)
    assert_equal(List(items), [4, 2])
    _ = items.pop(1)
    assert_equal(List(items), [4])
    _ = items.pop(0)
    assert_equal(List(items), [])

def test_equal() raises:
    var items1 = StaticIndexedList([4, 2, 1])
    var items2 = StaticIndexedList([4, 2, 1])
    var items3 = StaticIndexedList([4, 2])
    assert_true(items1 == items2)
    assert_true(items1 != items3)
    _ = items2.pop(2)
    print(items2)
    assert_true(items1 != items2)
    assert_true(items2 == items3)

def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()