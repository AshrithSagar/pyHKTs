# pyHKTs

(Experimental) Higher Kinded Types for Python3

This monorepo is a proof-of-concept implementation and testbed for adding native support for **Higher-Kinded Types (HKTs)** to Python's type system.
The long-term goal is to evolve this work towards a draft PEP.

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
    cls = type(obj)  # type[F]. Matches runtime, rather than type[F[A]] in the current python type system
    reveal_type(cls)  # type[F]

    tmp = (fn(a) for a in obj)
    spec_cls = cls[B]  # type[F[B]]. Go through the regular Generic specialisation through __class_getitem__, and GenericAlias at runtime
    reveal_type(spec_cls)  # type[F[B]]

    res = spec_cls(tmp)
    reveal_type(res)  # F[B]
    return res

    # In short, this is
    # return type(obj)(fn(a) for a in obj)
```
