# conformance/test_self_param.py

from typing import Callable, Generic, TypeVar, reveal_type

from typing_extensions import ParametricSelf

T = TypeVar("T")
B = TypeVar("B")


class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value: T = value

    def map(self, _fn: Callable[[T], B]) -> ParametricSelf[B]:
        raise NotImplementedError


class Bag(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value: T = value

    def map(self, _fn: Callable[[T], B]) -> ParametricSelf[B]:
        raise NotImplementedError


class SpecialBox(Box[T]):
    pass


if __name__ == "__main__":
    b: Box[int] = Box(42)
    reveal_type(b.map(str))  # Box[str]
    reveal_type(b.map(float))  # Box[float]
    reveal_type(b.map(str).map(len))  # Box[int]

    bag: Bag[str] = Bag("hello")
    reveal_type(bag.map(len))  # Bag[int]

    sb: SpecialBox[int] = SpecialBox(42)
    reveal_type(sb.map(str))  # SpecialBox[str]
