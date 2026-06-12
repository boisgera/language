

struct StaticLinkedListIter[T: Copyable & Writable, origin: Origin](Copyable, Iterator):
    comptime Element = Self.T
    var plist: Pointer[StaticLinkedList[Self.T], Self.origin]
    var current: Int

    def __init__(out self, ref[Self.origin] list: StaticLinkedList[Self.T]):
        self.plist = Pointer(to=list)
        self.current = self.plist[].head

    def __iter__(self) -> ref[self] Self:
        return self

    def __next__(mut self) raises StopIteration -> ref[self.plist[].list] Self.T:
        if self.current == StaticLinkedList[Self.T].NO_NEXT:
            raise StopIteration()
        ref list = self.plist[]
        ref value = list[self.current]
        self.current = list.next[self.current]
        return value



struct StaticLinkedList[T: Copyable & Writable](
    Boolable,
    Copyable,
    Iterable,
    Sized,
    Writable,
):
    var list: List[Self.T]
    var prev: List[Int]
    var next: List[Int]
    # var free: List[Bool] # TODO: maintain a free list?
    # var size: Int # TODO: cache the size (__len__ is expensive)
    var head: Int

    comptime IteratorType[
        iterable_mut: Bool, 
        //, 
        iterable_origin: Origin[mut=iterable_mut]
    ]: Iterator = StaticLinkedListIter[Self.T, iterable_origin]

    comptime NO_PREV = -1
    comptime NO_NEXT = -1
    comptime NO_HEAD = -1

    def __init__(out self, var list: List[Self.T]):
        self.list = list^
        self.prev = []
        self.next = []
        for i in range(len(self.list)):
            self.prev.append(i - 1)
            self.next.append(i + 1)
        if self.list:
            self.prev[0] = Self.NO_PREV
            self.next[len(self.list) - 1] = Self.NO_NEXT
            self.head = 0
        else:
            self.head = Self.NO_HEAD

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

    def write_to[WriterType: Writer](self, mut writer: WriterType):
        writer.write("[")
        for i, elt in enumerate(self):
            elt.write_to(writer)
            writer.write(", " if i < len(self) - 1 else "")
        writer.write("]")

    def __iter__(ref self) -> StaticLinkedListIter[Self.T, origin_of(self)]:
        return StaticLinkedListIter(self)

    def __len__(self) -> Int:
        if self.head == Self.NO_HEAD:
            return 0
        else:
            var count = 1
            var i = self.next[self.head]
            while i != Self.NO_NEXT:
                count += 1
                i = self.next[i] # Bug, out of bounds.
            return count

    def __bool__(self) -> Bool:
        return self.head != Self.NO_HEAD