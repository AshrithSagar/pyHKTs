# Prototype implementation

Regarding the submodules, every fork has a `pyhkts` branch where the changes are made.

On the type checker side, the reference implementations will be mainly for mypy, followed by pyright.

## cpython

The [`pyhkts` branch on the fork](https://github.com/AshrithSagar/cpython/tree/pyhkts) branches from the [`3.14` branch](https://github.com/python/cpython/tree/3.14).

Changes:
https://github.com/python/cpython/compare/3.14...AshrithSagar:cpython:pyhkts

- A new `TypeVarLike` introduced: `KindVar`.
- Currently implemented in `Lib/typing.py`.
  Can decide later if we want to implement it in C similar to `TypeVar`.
- There's also a `_KindApplication` object that deals with the runtime representation of applied higher kinded types.

## typing_extensions

Changes:
https://github.com/python/typing_extensions/compare/main...AshrithSagar:typing_extensions:pyhkts

- Backports `KindVar` and `_KindApplication`.

## typeshed

Changes:
https://github.com/python/typeshed/compare/main...AshrithSagar:typeshed:pyhkts

- Type stubs for `KindVar` and `_KindApplication`.

## mypy

Changes:
https://github.com/python/mypy/compare/master...AshrithSagar:mypy:pyhkts

- There's three new types added: `KindVarType`, `AppliedKindType`, and `KindTypeType`.

## pyright

Changes:
https://github.com/microsoft/pyright/compare/main...AshrithSagar:pyright:pyhkts

- Added `TypeCategory.KindApplication`, `KindApplicationType`.

## basedpyright

Changes:
https://github.com/detachhead/basedpyright/compare/main...AshrithSagar:basedpyright:pyhkts

- Changes are implemented in the pyright fork primarly.
  They can be synced here if no conflicts (done occasionally).
- This is not a priority as of now.

## peps

Changes:
https://github.com/python/peps/compare/main...AshrithSagar:peps:pyhkts

- No changes as of now, but eventually :)

---
