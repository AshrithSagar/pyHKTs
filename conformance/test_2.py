# conformance/test_2.py

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, KindVar, TypeVar, reveal_type

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")

F = KindVar("F", arity=1)


class Functor(Generic[F], ABC):
    @abstractmethod
    def map(self, fn: Callable[[A], B], fa: F[A]) -> F[B]:
        raise NotImplementedError

    def distribute(self, fab: F[tuple[A, B]]) -> tuple[F[A], F[B]]:
        return self.map(lambda t: t[0], fab), self.map(lambda t: t[1], fab)


class ListFunctor(Functor[list[Any]]):
    def map(self, fn: Callable[[A], B], fa: list[A]) -> list[B]:
        return list(fn(a) for a in fa)


if __name__ == "__main__":
    reveal_type(Functor.map)
    reveal_type(Functor[list[Any]].map)
    reveal_type(Functor.distribute)
    reveal_type(Functor[list[Any]].distribute)

    lf: ListFunctor = ListFunctor()
    dis = lf.distribute([(1, "1"), (2, "2")])
    reveal_type(dis)
