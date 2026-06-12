from train_tokenizer_fast import StaticLinkedList, StaticLinkedListIter

def main():
    # Build a list
    var data = [1, 2, 3, 4, 5]
    var sll = StaticLinkedList(data^)

    # String representation
    print("sll:", sll)

    # Basic iteration
    print("Forward:")
    for x in sll:
        print(x)

    # Remove middle element (index 2, value 3)
    sll.remove(2)
    print("After remove(2):")
    for x in sll:
        print(x)

    # Remove head (index 0, value 1)
    sll.remove(0)
    print("After remove(0):")
    for x in sll:
        print(x)

    # Remove tail (index 4, value 5)
    sll.remove(4)
    print("After remove(4):")
    for x in sll:
        print(x)

    # Length
    print("len:", len(sll))

    # Indexing
    print("sll[1]:", sll[1])   # value at storage index 1

    # Empty list
    var empty = StaticLinkedList[Int]([])
    print("empty len:", len(empty))
    print("empty has_next:", StaticLinkedListIter[Int, origin_of(empty)](empty).__has_next__())