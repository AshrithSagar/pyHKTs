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
