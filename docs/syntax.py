# This is a rough sketch of the syntax considerations,
# and a testbed to consider the possibilities on what to chose.
# FIXME: A Markdown file would be better for this. Convert to it later.

from collections.abc import Iterable, Mapping
from typing import Any, Generic, KindVar, Self, TypeVar, TypeVarTuple, Unpack

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")
Ts = TypeVarTuple("Ts")

TWithBound = TypeVar("TWithBound", bound=int)
TWithDefault = TypeVar("TWithDefault", default=int)
TWithBoundAndDefault = TypeVar("TWithBoundAndDefault", bound=int, default=int)


class Box_T(Generic[T]): ...


class Box_TWithBound(Generic[TWithBound]): ...


class Box_TWithDefault(Generic[TWithDefault]): ...


class Box_TWithBoundAndDefault(Generic[TWithBoundAndDefault]): ...


class Box_A_B(Generic[A, B]): ...


class Box_A_TWithDefault(Generic[A, TWithDefault]): ...


class Box_Ts(Generic[Unpack[Ts]]): ...


# ── [1] With KindVar introduced ───────────────────────────────────────────────

# KindVar declaration is quite similar to TypeVar.
# The first argument 'name' should match the variable name,
# and typecheckers can error if not, similar to TypeVar,
# and runtime shouldn't enforce this, similar to how TypeVar is handled.

## ── [1.1] KindVar ────────────────────────────────────────────────────────────

F1 = KindVar("F1")
# Unbound, and can take any arity.
# F1[T], F1[A, B], F1[*Ts], etc. are all valid.

### ── [1.1.1] KindVar with bounds ─────────────────────────────────────────────
# In this variation, the bound type parameters need not be specified.
# The arity should be inferred by the typechecker.

G1 = KindVar("G1", bound=Iterable)
# arity=1 should be inferred.
# G1[T], G1[A], etc. are valid.
# G1[A, B], G1[*Ts], etc. should be rejected.

G2 = KindVar("G2", bound=Mapping)
# arity=2 should be inferred.
# G2[A, B], etc. are valid.
# G2[T], G2[*Ts], etc. should be rejected.

# Additionally, we would also need to do away with errors such as:
# pyright: Expected type arguments for generic class "Iterable"

### ── [1.1.2] KindVar with bounds ─────────────────────────────────────────────
# In this variation, need to be explicit in type parameters when defining bounds.
# The arity inference should be from the bound class,
# and not from the arity of the type parameters specified.

H1 = KindVar("H1", bound=Iterable[T])
# arity=1 inferred from Iterable.
# And need to verify that upto one type parameter(s) are passed here.

H2 = KindVar("H2", bound=Mapping[A, B])
# arity=2 inferred from Mapping.
# And need to verify that upto two type parameter(s) are passed here.

# Mismatched arities should be rejected, they're already invalid.
H3 = KindVar("H3", bound=Iterable[A, B])  # Invalid

# TypeVar defaults should be respected, when valid.
H4 = KindVar("H4", bound=Box_A_TWithDefault[A])
H5 = KindVar("H5", bound=Box_TWithDefault)  # Invalid
H6 = KindVar("H6", bound=Box_TWithDefault[T])  # Fine

# ── [2] Reusing existing TypeVar ──────────────────────────────────────────────
# No KindVar introduced.
# TypeVar should accept an extra kwarg to denote kind.
# Can decide on an appropriate kwarg name.
# Suggestions: {arity, args, kind, ...}
# We shall stick to using 'arity' for now.

F1 = TypeVar("F1", arity=1)

# TypeVar subscripting should be allowed in the case of a type constructor.
# Regular TypeVar (i.e., no arity) should still emit an error when subscripted.

## ── [2.1] TypeVar with (explicit) arity ──────────────────────────────────────
# The arity kwarg is always required when we want to use the TypeVar as a type constructor.

## ── [2.2] TypeVar with (implicit) arity ──────────────────────────────────────
# The arity kwarg could be possibly optional in cases where we're able to infer it,
# such as when specifying with a bound.

# In the unbounded case, we have to mandatorily use the arity kwarg if wanting to specify a type constructor.

### ── [2.2.1] TypeVar with bounds and implicit arity ──────────────────────────
# In this variation, the bound type parameters need not be specified.
# The arity should be inferred by the typechecker.

G1 = TypeVar("G1", bound=Iterable)
# arity=1 should be inferred.
G2 = TypeVar("G2", bound=Mapping)
# arity=2 should be inferred.

# Additionally, we would also need to do away with errors such as:
# pyright: Expected type arguments for generic class "Iterable"

# This implicit inference could potentially lead to confusions when using, say bound=Iterable vs bound=Iterable[Any].
G3 = TypeVar("G3", bound=Iterable[Any])
# arity should not be inferred (or rather inferred to None). This is a regular TypeVar.

### ── [2.2.2] TypeVar with bounds and implicit arity ──────────────────────────
# In this variation, need to be explicit in type parameters when defining bounds.

H1 = TypeVar("H1", bound=Iterable[T])
H2 = TypeVar("H2", bound=Mapping[A, B])

# Additionally, we would also need to do away with errors such as:
# mypy: Type variable "T" is unbound. Mypy[valid-type]
# mypy:
#   (Hint: Use "Generic[T]" or "Protocol[T]" base class to bind "T" inside a class)
#   (Hint: Use "T" in function signature to bind "T" inside a function)
# pyright: TypeVar bound type cannot be generic
# pyright: Type variable "T" has no meaning in this context

# TypeVar defaults should be respected hopefully, when valid.
H3 = TypeVar("H3", bound=Box_A_TWithDefault[A])

# Although there might be some confusion when we're referring to a regular TypeVar vs a type constructor.

H4 = TypeVar("H4", bound=Box_TWithDefault)
# Possibly confusing but valid. A regular TypeVar.

H5 = TypeVar("H5", bound=Box_TWithDefault[T])
# Possibly confusing but valid. A type constructor.

# Mismatched arities should be rejected.
F4 = TypeVar("F4", bound=Iterable, arity=2)  # Invalid
F5 = TypeVar("F5", bound=Iterable[Any], arity=1)  # Invalid
F6 = TypeVar("F6", bound=Mapping, arity=3)  # Invalid


# ──────────────────────────────────────────────────────────────────────────────
# Compliance with PEP 544 – Protocols: Structural subtyping (static duck typing)

# TODO: Should have a clear specification here on how KindVars should behave in a Protocol.


# ──────────────────────────────────────────────────────────────────────────────
# Compliance with PEP 695 – Type Parameter Syntax

## Generic classes


# Unbounded case
# Not clear how to specify F as being a type constructor here, without requiring some parser and/or grammar changes.
class Bag1[T, F]: ...


## class Bag1[T, F[T]]: ...
# Something like this would prolly require some parser and maybe grammar changes. Seems plausible.

# Scala-like, using underscores. Prolly requires some parser and grammar changes.
## class Bag1[F[_]]: ...
## class Bag1[T, F[_]]: ...

# Or prefer the already existing Ellipsis. A bit confusing, but doesn't require much grammar changes.
# Not sure how this would come into play in types such as tuple[T, ...] that use Ellipsis.
# Would there be any conflicts? Should give this some more thought.
## class Bag1[F[...]]: ...
## class Bag1[T, F[...]]: ...


# In the bounded cases, only inference needs to be updated. This (bounded) case hopefully parses already.
# The inference with PEP 695 syntax depends on how the KindVar/TypeVar above is implemented.


# In this variation, the arity of the bound should be inferred. Related to [1.1.1].
class Bag2[T, F: Iterable]: ...


# There may be some dangers associated with this.


# Since, here F is a type, and in above F is a type constructor.
class Bag2[T, F: Iterable[Any]]: ...


# There may be some possible confusions that may silently arise if this syntax is chosen.


# This variation explicitly mentions type parameters in the bound. Related to [1.1.2].
class Bag2[T, F: Iterable[T]]: ...


# Depending on the complexity of the implementation, we can assess whether
# the order of the arguments should be strcitly enforced, or can be relaxed.
class Bag2[F: Iterable[T], T]: ...


# These variations depends on how the unbounded case with PEP 695 is handled.
class Bag2[T, F: Iterable[_]]: ...


class Bag2[T, F: Iterable[...]]: ...


## Generic functions and methods
# This is similar to how PEP 695 is handled for generic classes,
# and would follow from whatever syntax is finally decided upon there.


def fn1[T, F: Iterable](): ...


class Bag3[T, F: Iterable[T]]:
    def meth1[A](self, fn1: F[T], fn2: F[A]) -> None: ...

    # Here, T and F are from the class scope, and A is from the method scope.

    def meth2[A, G: Iterable[A]](self, fn1: F[T], fn2: G[A]) -> None: ...

    # Here, T and F are from the class scope, and A and G are from the method scope.

    # About patterns that mix these parameters,
    # it's not clear currently, since the syntax is not yet fixed.
    # These might not be a priority, in case these arise naturally as a consequence
    # in the implementation, then they're fine, otherwise we should avoid such patterns.
    # It's not clear what happens when you allow G: Iterable[A] vs G: Iterable
    def meth3[A, G: Iterable](self, fn1: F[A], fn2: G[T]) -> None: ...


# ──────────────────────────────────────────────────────────────────────────────
# Compliance with PEP 673 – Self Type

# Self implementation depends on how TypeVar/KindVar is handled.
# Subscriptable Self should be possible once that is resolved.

# One potentially confusing thing might be that if KindVar is favored instead of extending TypeVar,
# then subscriptable Self would become an implicit KindVar.
# For unsubscripted Self, we would prolly be continuing with the existing implicit TypeVar approach.
# So there may be some confusion/asymmetry with how this is handled.


class Bar1[T]:
    #
    ## The current understanding of Self:

    def meth1(self) -> Self: ...

    def meth1_explicit[Self: Bar1[Any]](self: Self) -> Self: ...

    #
    ## How Self should be modified to comply:

    def meth2_explicit[T, Self: Bar1[T]](self: Self[A]) -> Self[B]: ...

    # Does this T refer to the method scope or the outer class scope?
    # If we're being this explicit when translating.

    # T should prolly come from outer scope, which aligns to what's expected and done currently.
    def meth3_explicit[Self: Bar1[T]](self: Self[A]) -> Self[B]: ...


# ──────────────────────────────────────────────────────────────────────────────
### Other PEPs/features/interactions to keep in mind as well, although not a top priority, as of now:

## - Type variance

## - PEP 718 – Subscriptable functions
# This PEP is not yet accepted as of now, but could think if there may be any potential clashes here.

## - PEP 827 – Type Manipulation
# Also a WIP PEP. Need to look more on this.

## - How would the runtime typechecker scenario look like?

## - Would this allow better typing in functools, say functools.singledispatch?

# ──────────────────────────────────────────────────────────────────────────────
