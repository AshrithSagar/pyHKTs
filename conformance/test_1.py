# conformance/test_1.py

from collections.abc import Iterable
from typing import Callable, KindVar, TypeVar, reveal_type

T = TypeVar("T")
F = KindVar("F", bound=Iterable[T])
A = TypeVar("A")
B = TypeVar("B")


def fmap1(fn: Callable[[A], B], obj: F[A]) -> F[B]:
    reveal_type(obj)  # F[A]
    cls = type(obj)  # Should ideally be type[F], than type[F[A]], I think
    reveal_type(cls)
    tmp = (fn(a) for a in obj)
    spec_cls = cls[B]  # Should be type[F[B]]
    reveal_type(spec_cls)
    res = spec_cls(tmp)
    reveal_type(res)
    return res


def fmap2(fn: Callable[[A], B], obj: F[A]) -> F[B]:
    res = type(obj)(fn(a) for a in obj)
    reveal_type(res)
    return res
