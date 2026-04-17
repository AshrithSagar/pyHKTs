# Examples

> [!WARNING]
> WIP

```python
from collections.abc import Iterable
from typing import Callable, KindVar, TypeVar, reveal_type

T = TypeVar("T")
F = KindVar("F", bound=Iterable[T])
A = TypeVar("A")
B = TypeVar("B")


def fmap(fn: Callable[[A], B], obj: F[A]) -> F[B]:
    reveal_type(obj)  # F[A]
    cls = type(obj)  # type[F].
    # Matches runtime, rather than type[F[A]] in the current python type system.
    # It would be better to indicate this with, say a typing special form such as TypeConstructor[F] instead.
    reveal_type(cls)  # type[F]

    tmp = (fn(a) for a in obj)
    spec_cls = cls[B]  # type[F[B]].
    # Go through the regular Generic specialisation through __class_getitem__, and GenericAlias at runtime.
    # The typechecker need not be aware of the runtime implementation details,
    # it should just follow specialising such type constructors.
    reveal_type(spec_cls)  # type[F[B]]

    res = spec_cls(tmp)  # Should comply with __init__ of type[F[B]] (or rather type[F]) here.
    reveal_type(res)  # F[B]
    return res

    # In short, this is
    # return type(obj)(fn(a) for a in obj)
    #
    # type(obj)[B] is not required, it can possibly be inferred from the call site here.
```

See [conformance/test_1.py](../conformance/test_1.py).

---

```python
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, KindVar, TypeVar, reveal_type

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")

F = KindVar("F")


class Functor(Generic[F], ABC):
    @abstractmethod
    def map(self, fn: Callable[[A], B], fa: F[A]) -> F[B]:
        raise NotImplementedError

    # This can even come from a Mixin
    def distribute(self, fab: F[tuple[A, B]]) -> tuple[F[A], F[B]]:
        return self.map(lambda t: t[0], fab), self.map(lambda t: t[1], fab)


# Note: Can consider allowing Functor[list] to be valid, rather than Functor[list[Any]] here,
# since Functor(Generic[F]) is indicating to take a type constructor rather than a type.
class ListFunctor(Functor[list[Any]]):
    def map(self, fn: Callable[[A], B], fa: list[A]) -> list[B]:
        return list(fn(a) for a in fa)


reveal_type(Functor.map)  # def [F, A, B] (self: Functor[F], fn: def (A) -> B, fa: F[A]) -> F[B]
reveal_type(Functor[list[Any]].map)  # def [A, B] (self: Functor[list[Any]], fn: def (A) -> B, fa: list[A]) -> list[B]
reveal_type(Functor.distribute)  # def [F, A, B] (self: Functor[F], fab: F[tuple[A, B]]) -> tuple[F[A], F[B]]
reveal_type(Functor[list[Any]].distribute)  # def [A, B] (self: Functor[list[Any]], fab: list[tuple[A, B]]) -> tuple[list[A], list[B]]

lf: ListFunctor = ListFunctor()
dis = lf.distribute([(1, "1"), (2, "2")])
reveal_type(dis)  # tuple[list[int], list[str]]
```

See [conformance/test_2.py](../conformance/test_2.py), [conformance/test_3.py](../conformance/test_3.py).

---

## References

- _Functional Programming in Scala_ by Paul Chiusano and Rúnar Bjarnason
