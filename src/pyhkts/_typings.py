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
import re
import typing
from types import GenericAlias
from typing import Any, Generic, TypeAliasType, TypeVar, TypeVarTuple

from typing_extensions import TypeForm

_GenericAlias = typing._GenericAlias  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]


def is_generic(tp: TypeForm[Any]) -> bool:
    if isinstance(tp, (GenericAlias, _GenericAlias, TypeAliasType)):
        if len(getattr(tp, "__parameters__")) > 0:
            return True
        return False
    return hasattr(tp, "__class_getitem__")


def get_arity(tp: TypeForm[Any]) -> int:
    """
    arity -> Number of free type parameters, i.e., remaining/residual kind arity, and not total/construction arity.
    arity=-1 => Variadic
    arity=None => Unknown

    Don't know how to handle arity for builtins exactly: Currently pattern matching.
    """

    def is_variadic(params: tuple[Any, ...]) -> bool:
        for param in params:
            if isinstance(param, TypeVarTuple):
                return True
        return False

    if isinstance(tp, (GenericAlias, _GenericAlias)):
        parameters = getattr(tp, "__parameters__")
        if is_variadic(parameters):
            return -1
        return len(parameters)

    if isinstance(tp, TypeAliasType):
        type_params = getattr(tp, "__type_params__")
        if is_variadic(type_params):
            return -1
        return len(type_params)

    if hasattr(tp, "__class_getitem__"):
        parameters = getattr(tp, "__parameters__", None)
        if parameters is not None:
            if is_variadic(parameters):
                return -1
            return len(parameters)

    if is_generic(tp):
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
                # Either some builtins object (should add, then), or something else
                raise NotImplementedError
    else:
        # Non-generic classes (including builtins and user-defined)
        return 0


# ──────────────────────────────────────────────────────────────────────────────
# Quick tests


def main() -> None:
    T = TypeVar("T")
    A = TypeVar("A")
    B = TypeVar("B")
    Ts = TypeVarTuple("Ts")

    def _print_helper(tp: Any) -> None:
        def typ_to_str(tp: TypeForm[Any]) -> str:
            str_tp: str
            if isinstance(tp, type):
                str_tp = tp.__name__  # No need of "<class '...'>"
            else:
                str_tp = str(tp)  # Fallback
            str_tp = str_tp.replace("typing.", "")  # No need of "typing."...
            str_tp = str_tp.replace(f"{__name__}.", "")  # No need of module name
            str_tp = re.sub(r"Unpack\[(.*?)\]", r"*\1", str_tp)  # Unpack[...] -> *...
            return str_tp

        print(f"{typ_to_str(tp)}:")
        print(f" -> is_generic = {is_generic(tp)}")
        print(f" -> arity = {get_arity(tp)}")

    class B0: ...

    class B1(Generic[T]): ...

    type B2[*Ts] = tuple[int, *Ts, str]

    for typ in [
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
    ]:
        _print_helper(typ)


if __name__ == "__main__":
    main()
