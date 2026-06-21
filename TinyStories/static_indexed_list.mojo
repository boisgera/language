comptime Item = (
    Defaultable & Copyable & Equatable & ImplicitlyDestructible & Writable
)


def List_remove_first[T: Item](mut list: List[T], value: T):
    for i, elt in enumerate(list):
        if elt == value:
            _ = list.pop(i)
            return


struct StaticIndexedListIter[T: Item, origin: Origin](Iterator):
    comptime Element = Self.T
    var plist: Pointer[StaticIndexedList[Self.T], Self.origin]
    var index: Int

    def __init__(
        out self,
        ref[Self.origin] list: StaticIndexedList[Self.T],
        index: Int = 0,
    ):
        self.plist = Pointer(to=list)
        self.index = index

    def next(mut self) raises StopIteration -> ref[self.plist[].list] Self.T:
        ref list = self.plist[]
        if self.index > list.tail:
            raise StopIteration()
        ref value = list[self.index]
        self.index = list.next[self.index]
        return value

    def prev(mut self) raises StopIteration -> ref[self.plist[].list] Self.T:
        ref list = self.plist[]
        if self.index < list.head:
            raise StopIteration()
        ref value = list[self.index]
        self.index = list.prev[self.index]
        return value

    def __iter__(self) -> ref[self] Self:
        return self

    @always_inline
    def __next__(
        mut self,
    ) raises StopIteration -> ref[self.plist[].list] Self.T:
        return self.next()


comptime ListLike = (
    Boolable & Copyable & Equatable & Iterable & Sized & Writable
)


struct StaticIndexedList[T: Item](ListLike):
    var list: List[Self.T]
    var next: List[Int]
    var prev: List[Int]
    var head: Int
    var tail: Int
    var size: Int
    comptime IteratorType[
        iterable_mut: Bool,
        //,
        iterable_origin: Origin[mut=iterable_mut],
    ]: Iterator = StaticIndexedListIter[Self.T, iterable_origin]

    def __init__(out self, var list: List[Self.T]):
        self.next = List(range(1, len(list) + 1))
        self.prev = List(range(-1, len(list) - 1))
        self.head = 0
        self.tail = len(list) - 1
        self.size = len(list)
        self.list = list^

    def __getitem__(ref self, index: Int) -> ref[self.list] Self.T:
        return self.list[index]

    def __setitem__(mut self, index: Int, var value: Self.T):
        self.list[index] = value^

    def pop(mut self: Self, index: Int) -> Self.T:
        # ⚠️ will output garbage when is not valid anymore
        var t = Self.T()
        swap(self.list[index], t)
        var prev_index = self.prev[index]
        var next_index = self.next[index]
        if prev_index >= 0:
            self.next[prev_index] = next_index
        else:
            self.head = next_index
        if next_index < len(self):
            self.prev[next_index] = prev_index
        else:
            self.tail = prev_index
        self.size -= 1
        return t^

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

    @always_inline
    def __len__(self) -> Int:
        return self.size

    @always_inline
    def __bool__(self) -> Bool:
        return len(self) > 0
