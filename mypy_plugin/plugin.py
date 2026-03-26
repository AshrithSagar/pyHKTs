# mypy_plugin/plugin.py

from typing import Callable

from mypy.plugin import AnalyzeTypeContext, MethodContext, Plugin
from mypy.types import AnyType, Instance, ProperType, Type, TypeOfAny, get_proper_type

_PARAMETRIC_SELF_FULLNAME = "typing_extensions.ParametricSelf"
_SELF_FULLNAMES = {
    "typing.Self",
    "typing_extensions.Self",
}
_KINDVAR_FULLNAMES = {
    "typing.KindVar",
    "typing_extensions.KindVar",
}


class pyHKTsPlugin(Plugin):
    # ── Rule 1: KindVar in type position ─────────────────────────────────────
    # Teaches mypy that KindVar instances are valid as types.
    # Without this: "Variable F is not valid as a type"

    def get_type_analyze_hook(
        self, fullname: str
    ) -> Callable[[AnalyzeTypeContext], Type] | None:
        if fullname in _KINDVAR_FULLNAMES:
            return self._kindvar_as_type_hook
        return None

    def _kindvar_as_type_hook(self, ctx: AnalyzeTypeContext) -> Type:
        # Treat KindVar as Any for now — full inference comes later
        return AnyType(TypeOfAny.special_form)

    # ── Rule 2: Self[B] and ParametricSelf[B] in return position ─────────────
    # Substitutes Self[B] / ParametricSelf[B] with the receiver type
    # reparametrised with B.

    def get_method_hook(self, fullname: str) -> Callable[[MethodContext], Type] | None:
        return self._parametric_self_hook

    def _parametric_self_hook(self, ctx: MethodContext) -> Type:
        ret = get_proper_type(ctx.default_return_type)
        if not self._is_parametric_self(ret):
            return ctx.default_return_type
        self_type = get_proper_type(ctx.type)
        if not isinstance(self_type, Instance):
            return AnyType(TypeOfAny.special_form)
        assert isinstance(ret, Instance)
        if not ret.args:
            return AnyType(TypeOfAny.special_form)
        try:
            return Instance(
                self_type.type,
                list(ret.args),
                line=ret.line,
                column=ret.column,
            )
        except Exception:
            return AnyType(TypeOfAny.special_form)

    def _is_parametric_self(self, tp: ProperType) -> bool:
        if not isinstance(tp, Instance):
            return False
        fullname = tp.type.fullname
        return fullname == _PARAMETRIC_SELF_FULLNAME or fullname in _SELF_FULLNAMES


def plugin(version: str) -> type[pyHKTsPlugin]:
    return pyHKTsPlugin
