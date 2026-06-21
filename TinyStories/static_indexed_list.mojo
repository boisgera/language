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

    def __init__(out self, ref[Self.origin] list: StaticIndexedList[Self.T]):
        self.plist = Pointer(to=list)
        self.index = -1

    def next(mut self) raises StopIteration -> ref[self.plist[].list] Self.T:
        var new_index: Int
        if self.index < -1:
            new_index = 0  # first index
        else:
            new_index = self.index + 1
        if new_index >= len(self.plist[]):
            raise StopIteration()
        else:
            self.index = new_index
            return self.plist[][new_index]

    def prev(mut self) raises StopIteration -> ref[self.plist[].list] Self.T:
        var new_index: Int
        if self.index >= len(self.plist[]):
            new_index = len(self.plist[]) - 1  # last index
        else:
            new_index = self.index - 1
        if new_index < 0:
            raise StopIteration()
        else:
            self.index = new_index
            return self.plist[][new_index]

    def __iter__(self) -> ref[self] Self:
        return self

    @always_inline
    def __next__(
        mut self,
    ) raises StopIteration -> ref[self.plist[].list] Self.T:
        return self.next()


comptime ListLike = Boolable & Copyable & Equatable & Iterable & Sized & Writable


struct StaticIndexedList[T: Item](ListLike):
    var list: List[Self.T]
    var indices: List[Int] # Nah, we need some static stuff...
    # Or max indices a pair of (prev, next)
    # and then we're back to a dynamic computation of the size, that we 
    # may cache, we need a head and a tail, that we need to update, etc. 
    # call this list `prev_next`?
    comptime IteratorType[
        iterable_mut: Bool,
        //,
        iterable_origin: Origin[mut=iterable_mut],
    ]: Iterator = StaticIndexedListIter[Self.T, iterable_origin]

    def __init__(out self, var list: List[Self.T]):
        self.indices = List(range(len(list)))
        self.list = list^

    def __getitem__(ref self, index: Int) -> ref[self.list] Self.T:
        return self.list[index]

    def __setitem__(mut self, index: Int, var value: Self.T):
        self.list[index] = value^

    @always_inline
    def has_prev(self: Self, index: Int) -> Bool:
        return index > 0

    @always_inline
    def has_next(self: Self, index: Int) -> Bool:
        return index < len(self) - 1

    def pop(mut self: Self, index: Int) -> Self.T:
        # ⚠️ will output garbage when index is not in self.indices
        var t = Self.T()
        swap(self.list[index], t)
        List_remove_first(self.indices, index)
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
        return len(self.list)

    @always_inline
    def __bool__(self) -> Bool:
        return len(self) > 0
