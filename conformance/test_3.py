# conformance/test_3.py

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, KindVar, TypeVar, reveal_type

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

F = KindVar("F")
M = KindVar("M")


# ── Functor ────────────────────────────────────────────────────────────────────


class Functor(Generic[F], ABC):
    @abstractmethod
    def map(self, fn: Callable[[A], B], fa: F[A]) -> F[B]:
        raise NotImplementedError

    def distribute(self, fab: F[tuple[A, B]]) -> tuple[F[A], F[B]]:
        return self.map(lambda t: t[0], fab), self.map(lambda t: t[1], fab)

    def replace(self, b: B, fa: F[A]) -> F[B]:
        return self.map(lambda _: b, fa)


# ── Apply (Functor + ap) ───────────────────────────────────────────────────────


class Apply(Functor[F], ABC):
    @abstractmethod
    def ap(self, ff: F[Callable[[A], B]], fa: F[A]) -> F[B]:
        raise NotImplementedError

    def map2(self, fn: Callable[[A, B], C], fa: F[A], fb: F[B]) -> F[C]:
        return self.ap(self.map(lambda a: lambda b: fn(a, b), fa), fb)


# ── Applicative (Apply + pure) ─────────────────────────────────────────────────


class Applicative(Apply[F], ABC):
    @abstractmethod
    def pure(self, a: A) -> F[A]:
        raise NotImplementedError

    def when(self, cond: bool, fa: F[None]) -> F[None]:
        if cond:
            return fa
        return self.pure(None)


# ── Monad (Applicative + flatMap) ──────────────────────────────────────────────


class Monad(Applicative[F], ABC):
    @abstractmethod
    def flat_map(self, fa: F[A], fn: Callable[[A], F[B]]) -> F[B]:
        raise NotImplementedError

    def flatten(self, ffa: F[F[A]]) -> F[A]:
        return self.flat_map(ffa, lambda fa: fa)

    def map(self, fn: Callable[[A], B], fa: F[A]) -> F[B]:
        return self.flat_map(fa, lambda a: self.pure(fn(a)))

    def ap(self, ff: F[Callable[[A], B]], fa: F[A]) -> F[B]:
        return self.flat_map(ff, lambda f: self.map(f, fa))

    def compose(
        self,
        f: Callable[[A], F[B]],
        g: Callable[[B], F[C]],
    ) -> Callable[[A], F[C]]:
        return lambda a: self.flat_map(f(a), g)


# ── Foldable ───────────────────────────────────────────────────────────────────


class Foldable(Generic[F], ABC):
    @abstractmethod
    def fold_left(self, fa: F[A], z: B, fn: Callable[[B, A], B]) -> B:
        raise NotImplementedError

    def to_list(self, fa: F[A]) -> list[A]:
        return self.fold_left(fa, [], lambda acc, a: acc + [a])

    def length(self, fa: F[A]) -> int:
        return self.fold_left(fa, 0, lambda acc, _: acc + 1)

    def exists(self, fa: F[A], pred: Callable[[A], bool]) -> bool:
        return self.fold_left(fa, False, lambda acc, a: acc or pred(a))

    def forall(self, fa: F[A], pred: Callable[[A], bool]) -> bool:
        return self.fold_left(fa, True, lambda acc, a: acc and pred(a))


# ── Traversable (Functor + Foldable + traverse) ────────────────────────────────


class Traversable(Functor[F], Foldable[F], ABC):
    @abstractmethod
    def traverse(
        self,
        app: Applicative[M],
        fn: Callable[[A], M[B]],
        fa: F[A],
    ) -> M[F[B]]:
        raise NotImplementedError

    def sequence(self, app: Applicative[M], fma: F[M[A]]) -> M[F[A]]:
        return self.traverse(app, lambda ma: ma, fma)


# ── List instances ─────────────────────────────────────────────────────────────


class ListFunctor(Functor[list[Any]]):
    def map(self, fn: Callable[[A], B], fa: list[A]) -> list[B]:
        return [fn(a) for a in fa]


class ListMonad(Monad[list[Any]]):
    def flat_map(self, fa: list[A], fn: Callable[[A], list[B]]) -> list[B]:
        return [b for a in fa for b in fn(a)]

    def pure(self, a: A) -> list[A]:
        return [a]


class ListFoldable(Foldable[list[Any]]):
    def fold_left(self, fa: list[A], z: B, fn: Callable[[B, A], B]) -> B:
        acc = z
        for a in fa:
            acc = fn(acc, a)
        return acc


class ListTraversable(Traversable[list[Any]]):
    def map(self, fn: Callable[[A], B], fa: list[A]) -> list[B]:
        return [fn(a) for a in fa]

    def traverse(
        self,
        app: Applicative[M],
        fn: Callable[[A], M[B]],
        fa: list[A],
    ) -> M[list[B]]:
        result: M[list[B]] = app.pure([])
        for a in fa:
            mb = fn(a)
            result = app.map2(lambda acc, b: acc + [b], result, mb)
        return result

    def fold_left(self, fa: list[A], z: B, fn: Callable[[B, A], B]) -> B:
        acc = z
        for a in fa:
            acc = fn(acc, a)
        return acc


# ── Smoke tests ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Functor
    reveal_type(Functor.map)
    reveal_type(Functor[list[Any]].map)
    reveal_type(Functor.distribute)
    reveal_type(Functor[list[Any]].distribute)

    # Apply / Applicative
    reveal_type(Apply.ap)
    reveal_type(Apply[list[Any]].ap)
    reveal_type(Applicative.pure)
    reveal_type(Applicative[list[Any]].pure)

    # Monad
    reveal_type(Monad.flat_map)
    reveal_type(Monad[list[Any]].flat_map)
    reveal_type(Monad.compose)
    reveal_type(Monad[list[Any]].compose)

    # Foldable
    reveal_type(Foldable.fold_left)
    reveal_type(Foldable[list[Any]].fold_left)
    reveal_type(Foldable.to_list)

    # Traversable
    reveal_type(Traversable.traverse)
    reveal_type(Traversable[list[Any]].traverse)

    # ListMonad
    lm: ListMonad = ListMonad()
    reveal_type(lm.pure(42))
    reveal_type(lm.flat_map([1, 2, 3], lambda x: [x, x * 10]))
    reveal_type(lm.map(str, [1, 2, 3]))
    reveal_type(lm.map2(lambda a, b: a + b, [1, 2], [3, 4]))
    reveal_type(lm.compose(lambda x: [x, x], lambda x: [x * 10])(5))

    # ListFoldable
    lf: ListFoldable = ListFoldable()
    reveal_type(lf.to_list([1, 2, 3]))
    reveal_type(lf.length([1, 2, 3]))
    reveal_type(lf.exists([1, 2, 3], lambda x: x > 2))

    # ListFunctor
    lfunc: ListFunctor = ListFunctor()
    dis = lfunc.distribute([(1, "1"), (2, "2")])
    reveal_type(dis)
