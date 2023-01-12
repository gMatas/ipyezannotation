class IndexCounter:
    def __init__(self, length: int, start: int = 0, circular: bool = False):
        self.circular = circular
        self._length = length
        self._index = start

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int) -> None:
        if not (0 <= value < self._length):
            raise IndexError(f"New index is not within valid range of [0 to {self._length}).")

        self._index = value

    @property
    def length(self) -> int:
        return self._length

    def step(self, by: int) -> None:
        index = self._index + by
        if self.circular:
            if self._length == 1:
                index = 0
            if index >= self._length:
                index %= self._length
            elif index < 0:
                index = self._length - (-index % self._length)
        elif index >= self._length:
            raise IndexError(
                f"Can't move {by=}, since number of "
                f"available items is {self._length}."
            )

        self._index = index
