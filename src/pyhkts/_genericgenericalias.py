"""
Generic types.GenericAlias
=======
See https://github.com/python/typing/issues/548#issuecomment-2357252461

`GenericGenericAlias` behaves something like `Apply`.
`Apply[Base, Args]` <--> `Base[Args]`.

Type checkers can be taught to unify and reduce as such, prolly.
"""
# src/pyhkts/_genericgenericalias.py

# pyright: reportAny = false
# pyright: reportExplicitAny = false
# pyright: reportMissingTypeArgument = false

from types import GenericAlias
from typing import Any, Self, cast, get_args, override, reveal_type

from typing_extensions import TypeForm


class GenericGenericAlias1[
    Origin = None,
    *Args = *tuple[Any, ...],
](GenericAlias):
    def __new__(cls, origin: type[Origin], *args: *Args) -> Self:
        return super().__new__(cls, origin, args)

    @property
    @override
    def __origin__(self) -> type[Origin]:
        return cast(type[Origin], super().__origin__)

    @property
    @override
    def __args__(self) -> tuple[*Args]:
        return cast(tuple[*Args], super().__args__)


class GenericGenericAlias2[
    Origin = None,
    Args: tuple[Any, ...] = tuple[Any, ...],
](GenericAlias):
    def __new__(cls, origin: type[Origin], args: TypeForm[Args], /) -> Self:
        _args: tuple[Any, ...] = get_args(args)
        return super().__new__(cls, origin, _args)

    @property
    @override
    def __origin__(self) -> type[Origin]:
        return cast(type[Origin], super().__origin__)

    @property
    @override
    def __args__(self) -> Args:
        return cast(Args, super().__args__)


# ──────────────────────────────────────────────────────────────────────────────
# Quick tests

a1: GenericGenericAlias1[list[int], type[int]] = GenericGenericAlias1(list, int)
print(a1)  # list[int]

a2: GenericGenericAlias2[list[int], tuple[int]] = GenericGenericAlias2(list, tuple[int])
print(a2)  # list[int]


b1: GenericGenericAlias1[
    dict[int, str],
    type[int],
    type[str],
] = GenericGenericAlias1(dict, int, str)
print(b1)  # dict[int, str]

b2: GenericGenericAlias2[
    dict[int, str],
    tuple[int, str],
] = GenericGenericAlias2(dict, tuple[int, str])
print(b2)  # dict[int, str]

reveal_type(b2.__origin__)  # Runtime type is 'type'
print(b2.__origin__)  # <class 'dict'>

reveal_type(dict[int, str])  # Runtime type is 'GenericAlias'
print(dict[int, str])  # dict[int, str]


class MyInt(int): ...


c2: GenericGenericAlias2[
    dict[int, str],
    tuple[int, str],
] = GenericGenericAlias2(dict, tuple[MyInt, str])
print(c2)  # dict[MyInt, str]
