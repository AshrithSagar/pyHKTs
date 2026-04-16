"""
Typing experiments
=======
Ideally, some of these should reside in typing.py
"""
# src/pyhkts/_typings.py

# mypy: disable-error-code="misc, valid-type"
# pyright: reportAny = false
# pyright: reportExplicitAny = false
# pyright: reportGeneralTypeIssues = false

import builtins
import typing
from types import GenericAlias
from typing import (
    Any,
    TypeAliasType,
    TypeGuard,
    TypeVar,
    TypeVarTuple,
    Unpack,
    get_args,
    get_origin,
)

from typing_extensions import TypeForm

_GenericAlias = typing._GenericAlias  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]


def _is_typevar(x: Any) -> TypeGuard[TypeVar]:
    return isinstance(x, TypeVar)


def _is_typevartuple(x: Any) -> TypeGuard[TypeVarTuple]:
    return isinstance(x, TypeVarTuple)


def _is_unpack(x: Any) -> bool:
    return get_origin(x) is Unpack


def _has_variadic(args: tuple[Any, ...]) -> bool:
    for a in args:
        if _is_typevartuple(a):
            return True
        if _is_unpack(a):
            inner = get_args(a)
            if inner and _is_typevartuple(inner[0]):
                return True
    return False


def is_generic(tp: TypeForm[Any] | GenericAlias | TypeAliasType) -> bool:
    """
    is_generic -> "has free type parameters", not "is a generic type constructor".
    """

    origin = get_origin(tp)

    # Parametrised generics, like list[int]
    if origin is not None:
        args = get_args(tp)
        return any(_is_typevar(a) or _is_typevartuple(a) or _is_unpack(a) for a in args)

    # TypeAliasType
    if isinstance(tp, TypeAliasType):
        params = getattr(tp, "__type_params__", ())
        return len(params) > 0

    # Bare generics, like list, dict
    return hasattr(tp, "__class_getitem__")


def get_arity(tp: TypeForm[Any] | GenericAlias | TypeAliasType) -> int:
    """
    arity -> Number of free type parameters, i.e., remaining/residual kind arity, and not total/construction arity.
    arity=-1 => Variadic
    arity=0 => Fully applied / Non-generic

    Don't know how to handle arity for builtins exactly: Currently pattern matching.
    """

    origin = get_origin(tp)

    # Parametrised generics
    if origin is not None:
        args = get_args(tp)
        if _has_variadic(args):
            return -1
        return sum(1 for a in args if _is_typevar(a))

    # TypeAliasType
    if isinstance(tp, TypeAliasType):
        params = getattr(tp, "__type_params__", ())
        if _has_variadic(params):
            return -1
        return len(params)

    # Bare builtins
    if hasattr(tp, "__class_getitem__"):
        match tp:
            case builtins.list:
                return 1
            case builtins.set:
                return 1
            case builtins.dict:
                return 2
            case builtins.tuple:
                return -1
            case _:
                # User-defined generic class
                params = getattr(tp, "__parameters__", ())
                if _has_variadic(params):
                    return -1
                return len(params)

    # Non-generic
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# Quick tests


def main() -> None:
    import re
    from typing import Generic, TypeVar

    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    console = Console()
    table = Table()
    table.add_column("Type", style="bold cyan")
    table.add_column("Generic?", justify="center")
    table.add_column("Arity", justify="center")

    def _typ_to_str(tp: TypeForm[Any] | GenericAlias | TypeAliasType) -> str:
        str_tp: str
        if isinstance(tp, type):
            str_tp = tp.__name__  # No need of "<class '...'>"
        else:
            str_tp = str(tp)  # Fallback
        str_tp = str_tp.replace("typing.", "")  # No need of "typing."...
        str_tp = str_tp.replace(f"{__name__}.", "")  # No need of module name
        str_tp = str_tp.split(".")[-1]  # No need of paths
        str_tp = re.sub(r"Unpack\[(.*?)\]", r"*\1", str_tp)  # Unpack[...] -> *...
        return str_tp

    ##

    T = TypeVar("T")
    A = TypeVar("A")
    B = TypeVar("B")
    Ts = TypeVarTuple("Ts")

    class B0: ...

    class B1(Generic[T]): ...

    type B2[*Ts] = tuple[int, *Ts, str]

    for typ in list[TypeForm[Any] | GenericAlias | TypeAliasType]([
        int,
        #
        list,
        list[T],
        list[int],
        list[Any],
        #
        dict,
        dict[A, B],
        dict[int, T],
        dict[int, str],
        #
        tuple,
        tuple[T],
        tuple[int],
        tuple[A, B],
        tuple[int, T],
        tuple[int, str],
        tuple[*Ts],
        tuple[int, *Ts],
        #
        B0,
        #
        B1,
        B1[T],
        B1[int],
        #
        B2,
        B2[int],
        B2[*Ts],
        B2[int, *Ts],
    ]):
        table.add_row(
            Text(_typ_to_str(typ)),
            str(is_generic(typ)),
            str(get_arity(typ)),
        )
    console.print(table)


if __name__ == "__main__":
    main()
