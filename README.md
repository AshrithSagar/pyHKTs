# pyHKTs

(Experimental) Higher Kinded Types for Python3

The aim of this monorepo is to draft a PEP towards **Higher-Kinded Types (HKTs)** in Python's type system, along with a prototype implementation.

See [docs/](docs/) for the design notes and more info.

## Setup

<details>

<summary>Install uv (recommended)</summary>

Install [`uv`](https://docs.astral.sh/uv/), if not already.
Check [here](https://docs.astral.sh/uv/getting-started/installation/) for installation instructions.

**TL;DR: Just run**

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

<details>

<summary>Setup the monorepo</summary>

1. Clone the repo along with all the submodules.

   ```shell
   git clone --recurse-submodules https://github.com/AshrithSagar/pyHKTs.git

   cd pyHKTs
   ```

2. Setup and build the custom `cpython`. Refer to the official docs [here](https://devguide.python.org/getting-started/setup-building/).

   **TL;DR:**

   ```shell
   cd cpython

   ./configure --with-pydebug

   make -s -j $(nproc)
   ```

   The debug build provides the python executable at `./python` on most machines (or `./python.exe` on macOS).

3. Setup the workspace

   ```shell
   cd ..

   uv sync --all-groups --python=cpython/python.exe
   ```

</details>

# Examples

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
