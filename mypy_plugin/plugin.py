# mypy_plugin/plugin.py

from typing import Callable

from mypy.plugin import MethodContext, Plugin
from mypy.types import AnyType, Instance, ProperType, Type, TypeOfAny, get_proper_type

_PARAMETRIC_SELF_FULLNAME = "typing_extensions.ParametricSelf"


class pyHKTsPlugin(Plugin):
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
        return (
            isinstance(tp, Instance) and tp.type.fullname == _PARAMETRIC_SELF_FULLNAME
        )


def plugin(version: str) -> type[pyHKTsPlugin]:
    return pyHKTsPlugin
