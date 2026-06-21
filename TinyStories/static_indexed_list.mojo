from std.iter import zip

comptime Item = Defaultable & Copyable & Equatable &ImplicitlyDestructible & Writable

struct StaticIndexedListIter[T: Item, origin: Origin](Iterator):
    comptime Element = Self.T
    var plist: Pointer[StaticIndexedList[Self.T], Self.origin]
    var current: Int

    def __init__(out self, ref[Self.origin] list: StaticIndexedList[Self.T]):
        self.plist = Pointer(to=list)
        self.current = self.plist[].head

    def __iter__(self) -> ref[self] Self:
        return self

    def __next__(
        mut self,
    ) raises StopIteration -> ref[self.plist[].list] Self.T:
        if self.current == StaticIndexedList[Self.T].NO_NEXT:
            raise StopIteration()
        ref list = self.plist[]
        ref value = list[self.current]
        self.current = list.next[self.current]
        return value


comptime ListLike = Boolable & Copyable & Equatable & Iterable & Sized & Writable

# TODO: get rid of prev and next lists, instead maintain a list of used indices.
struct StaticIndexedList[T: Item](ListLike):
    var list: List[Self.T]
    var prev: List[Int]
    var next: List[Int]
    # var free: List[Bool] # TODO: maintain a free list?
    # var size: Int # TODO: cache the size (__len__ is expensive)
    var head: Int

    comptime IteratorType[
        iterable_mut: Bool, //, iterable_origin: Origin[mut=iterable_mut]
    ]: Iterator = StaticIndexedListIter[Self.T, iterable_origin]

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

    def has_prev(self: Self, index: Int) -> Bool:
        return self.prev[index] != Self.NO_PREV

    def has_next(self: Self, index: Int) -> Bool:
        return self.next[index] != Self.NO_NEXT

    def pop(mut self: Self, index: Int) -> Self.T:
        var t = Self.T()
        swap(self.list[index], t)

        var p = self.prev[index]
        var n = self.next[index]
        if p != Self.NO_PREV:
            self.next[p] = n
        else:
            self.head = n
        if n != Self.NO_NEXT:
            self.prev[n] = p

        return t^

    def remove(mut self, index: Int):
        _ = self.pop(index)

    def write_to[WriterType: Writer](self, mut writer: WriterType):
        writer.write("[")
        for i, elt in enumerate(self):
            elt.write_to(writer)
            writer.write(", " if i < len(self) - 1 else "")
        writer.write("]")

    def __eq__(self: Self, other: Self) -> Bool:
        if len(self) != len(other):
            return False
        for elt1, elt2 in zip(self, other):
            if elt1 != elt2:
                return False
        return True

    def __iter__(ref self) -> StaticIndexedListIter[Self.T, origin_of(self)]:
        return StaticIndexedListIter(self)

    def __len__(self) -> Int:
        if self.head == Self.NO_HEAD:
            return 0
        else:
            var count = 1
            var i = self.next[self.head]
            while i != Self.NO_NEXT:
                count += 1
                i = self.next[i]  # Bug, out of bounds.
            return count

    def __bool__(self) -> Bool:
        return self.head != Self.NO_HEAD
