# Syntax

This is a rough sketch of the syntax considerations,
and a testbed to consider the possibilities on what to chose.

Some definitions that will be resued in this doc:

```python
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
```

## A new primitive: `typing.KindVar`

`KindVar` declaration is quite similar to `TypeVar`.
The first argument '`name`' should match the variable name, and typecheckers can error if not, similar to `TypeVar`, and runtime shouldn't enforce this, similar to how `TypeVar` is handled.

```python
F1 = KindVar("F1")
# Unbound, and can take any arity.
# F1[T], F1[A, B], F1[*Ts], etc. are all valid.
```

### Bounds

#### Variation-1

In this variation, the bound type parameters need not be specified.
The arity should be inferred by the type checker.

```python
G1 = KindVar("G1", bound=Iterable)
# arity=1 should be inferred.
# G1[T], G1[A], etc. are valid.
# G1[A, B], G1[*Ts], etc. should be rejected.

G2 = KindVar("G2", bound=Mapping)
# arity=2 should be inferred.
# G2[A, B], etc. are valid.
# G2[T], G2[*Ts], etc. should be rejected.
```

Additionally, we would also need to do away with errors such as:

- `pyright`: Expected type arguments for generic class "Iterable"

#### Variation-2

In this variation, need to be explicit in type parameters when defining bounds.
The arity inference should be from the bound class,
and not from the arity of the type parameters specified.

```python
H1 = KindVar("H1", bound=Iterable[T])
# arity=1 inferred from Iterable.
# And need to verify that upto one type parameter(s) are passed here.

H2 = KindVar("H2", bound=Mapping[A, B])
# arity=2 inferred from Mapping.
# And need to verify that upto two type parameter(s) are passed here.
```

Mismatched arities should be rejected, they're already invalid.

```python
H3 = KindVar("H3", bound=Iterable[A, B]) # Invalid
```

`TypeVar` defaults should be respected, when valid.

```python
H4 = KindVar("H4", bound=Box_A_TWithDefault[A])
H5 = KindVar("H5", bound=Box_TWithDefault) # Invalid
H6 = KindVar("H6", bound=Box_TWithDefault[T]) # Fine
```

## Reusing existing `TypeVar`: with an `arity` kwarg

No `KindVar` introduced.
`TypeVar` should accept an extra kwarg to denote kind.
Can decide on an appropriate kwarg name.
Suggestions: {arity, args, kind, ...}.
We shall stick to using 'arity' for now.

```python
F1 = TypeVar("F1", arity=1)
```

`TypeVar` subscripting should be allowed in the case of a type constructor.
Regular `TypeVar`s (i.e., no arity) should still emit an error when subscripted.

### TypeVar with (explicit) arity

The arity kwarg is always required when we want to use the `TypeVar` as a type constructor.

### TypeVar with (implicit) arity

The arity kwarg could be possibly optional in cases where we're able to infer it, such as when specifying with a bound.

In the unbounded case, we have to mandatorily use the arity kwarg if wanting to specify a type constructor.

#### TypeVar with bounds and implicit arity (Variation-1)

In this variation, the bound type parameters need not be specified.
The arity should be inferred by the type checker.

```python
G1 = TypeVar("G1", bound=Iterable)
# arity=1 should be inferred.

G2 = TypeVar("G2", bound=Mapping)
# arity=2 should be inferred.
```

Additionally, we would also need to do away with errors such as:

- `pyright`: Expected type arguments for generic class "Iterable"

This implicit inference could potentially lead to confusions when using, say `bound=Iterable` vs `bound=Iterable[Any]`.

```python
G3 = TypeVar("G3", bound=Iterable[Any])
# arity should not be inferred (or rather inferred to None). This is a regular TypeVar.
```

#### TypeVar with bounds and implicit arity (Variation-2)

In this variation, need to be explicit in type parameters when defining bounds.

```python
H1 = TypeVar("H1", bound=Iterable[T])
H2 = TypeVar("H2", bound=Mapping[A, B])
```

Additionally, we would also need to do away with errors such as:

- `mypy`:
  Type variable "T" is unbound. Mypy[valid-type]

- `mypy`:
  (Hint: Use "Generic[T]" or "Protocol[T]" base class to bind "T" inside a class)
  (Hint: Use "T" in function signature to bind "T" inside a function)

- `pyright`:
  TypeVar bound type cannot be generic

- `pyright`:
  Type variable "T" has no meaning in this context

`TypeVar` defaults should be respected hopefully, when valid.

```python
H3 = TypeVar("H3", bound=Box_A_TWithDefault[A])
```

Although there might be some confusion when we're referring to a regular `TypeVar` vs a type constructor.

```python
H4 = TypeVar("H4", bound=Box_TWithDefault)
# Possibly confusing but valid. A regular TypeVar.

H5 = TypeVar("H5", bound=Box_TWithDefault[T])
# Possibly confusing but valid. A type constructor.
```

Mismatched arities should be rejected.

```python
F4 = TypeVar("F4", bound=Iterable, arity=2) # Invalid
F5 = TypeVar("F5", bound=Iterable[Any], arity=1) # Invalid
F6 = TypeVar("F6", bound=Mapping, arity=3) # Invalid
```

## Compliance with PEP 544 – Protocols: Structural subtyping (static duck typing)

TODO:
Should have a clear specification here on how `KindVar`s should behave in a `Protocol`.

## Compliance with PEP 695 – Type Parameter Syntax

### Generic classes

#### Unbounded case

Not clear how to specify `F` as being a type constructor here, without requiring some parser and/or grammar changes.

```python
class Bag1[T, F]: ...
```

```python
class Bag1[T, F[T]]: ...
# Something like this would prolly require some parser and maybe grammar changes. Seems plausible.
```

```python
# Scala-like, using underscores.
# Prolly requires some parser and grammar changes.
class Bag1[F[_]]: ...
class Bag1[T, F[_]]: ...
```

```python
# Or prefer the already existing Ellipsis.
# A bit confusing, but doesn't require much grammar changes.
# Since Ellipsis would be the first argument in such a definition for kind variables, it prolly shouldn't be a problem to differentiate it with types such as tuple[T, ...].
class Bag1[F[...]]: ...
class Bag1[T, F[...]]: ...
```

#### Bounded case

In the bounded cases, only inference needs to be updated.
These cases hopefully parses already.
The inference with PEP 695 syntax depends on how the `KindVar`/`TypeVar` above is implemented.

##### Variation-1

In this variation, the arity of the bound should be inferred.
Related to Variation-1 in `KindVar` with bounds.

```python
class Bag2[T, F: Iterable]: ...
```

There may be some dangers associated with this.
Since, here `F` is a type, and in above `F` is a type constructor.

```python
class Bag2[T, F: Iterable[Any]]: ...
```

There may be some possible confusions that may silently arise if this syntax is chosen.

##### Variation-2

This variation explicitly mentions type parameters in the bound.
Related to Variation-2 in `KindVar` with bounds.

```python
class Bag2[T, F: Iterable[T]]: ...
```

Depending on the complexity of the implementation, we can assess whether the order of the arguments should be strcitly enforced, or can be relaxed.

```python
class Bag2[F: Iterable[T], T]: ...
```

##### Variation-3

These variations depends on how the unbounded case with PEP 695 is handled.

```python
class Bag2[T, F: Iterable[_]]: ...

class Bag2[T, F: Iterable[...]]: ...
```

### Generic functions and methods

This is similar to the previous section on how PEP 695 is handled for generic classes, and would follow from whatever syntax is finally decided upon there.

```python
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
```

## Compliance with PEP 673 – Self Type

`Self` implementation depends on how `TypeVar`/`KindVar` is handled.
Subscriptable `Self` should be possible once that is resolved.
One potentially confusing thing might be that if `KindVar` is favored instead of extending `TypeVar`, then subscriptable `Self` would become an implicit `KindVar`.
For unsubscripted `Self`, we would prolly be continuing with the existing implicit `TypeVar` approach.
So there may be some confusion/asymmetry with how this is handled.

```python
class Bar1[T]:
    #
    ## The current understanding of Self:

    def meth1(self) -> Self: ...

    # The above roughly translates to:

    def meth1_explicit[Self: Bar1[Any]](self: Self) -> Self: ...

    #
    ## How Self should be modified to comply:

    def meth2_explicit[T, Self: Bar1[T]](self: Self[A]) -> Self[B]: ...

    # Does this T refer to the method scope or the outer class scope?
    # If we're being this explicit when translating.

    # T should prolly come from outer scope, which aligns to what's expected and done currently.
    def meth3_explicit[Self: Bar1[T]](self: Self[A]) -> Self[B]: ...
```

## Reusing existing `TypeVar`: allowing generic bounds

We can allow `TypeVar` bounds to be generic.

```python
F1 = TypeVar("F1", bound=Generic[T])
# Unbounded, arity=1 kind variable

F2 = TypeVar("F2", bound=Iterable[T])
# Upper bounded by Iterable, arity=1 kind variable

F3 = TypeVar("F3", bound=Generic[Unpack[Ts]])
# Unbounded, variadic kind variable
```

`TypeVar.__getitem__` must be allowed for such cases.
Type checkers should still catch the cases (i.e., present behaviour) when we try to subscript a `TypeVar` when not defined as above.

This also plays well with PEP 695, and requires no grammar change.

```python
def fmap[F: Generic[T], A, B](fn: Callable[[A], B], fa: F[A]) -> F[B]: ...
```

It is unclear what to do with `T`.

There are a few possibilites:

```python
def fmap[T, F: Generic[T], A, B](fn: Callable[[A], B], fa: F[A]) -> F[B]: ...

def fmap[F: Generic, A, B](fn: Callable[[A], B], fa: F[A]) -> F[B]: ...
```

Also, in the above cases, it's unclear what the implementation of the function would be, if the bound is just `Generic`.
We would need more restriction, to something like `Iterable`, say, to make use of it.

One problem with `Iterable` is that we're unaware of what the signature for the constructor call is (`Iterable` only specifies `__iter__`, and we don't know the `__new__` and/or `__init__`).
So, we need a better protocol, or say, with intersection types have constructor call be specified somehow.

So, if we tried to introduce a `typing` primitive, say `TypeConstructor`, which behaves as

```python
def fmap[F: TypeConstructor[tuple[Any]], A, B](fn: Callable[[A], B], fa: F[A]) -> F[B]: ...
```

i.e., `F: TypeConstructor[tuple[Any]]` means `F[A]`, `F[B]`, etc are valid (arity=1).

Similarly, `F: TypeConstructor[tuple[Any, ...]]` means `F[A]`, `F[A, B]`, `F[*Ts]`, etc are valid (variadic arity).

The corresponding `TypeVar` bounds can be specified in this way also, say `F: TypeConstructor[tuple[int, str]]`, which means when applied, `F[A, B]` is only valid when `TypeVar` `A` is bounded by `int`, and `TypeVar` `B` is bounded by `str`, and so on.

Maybe for brevity, we can also consider to remove the `tuple[]` and directly use `TypeConstructor[]` (it's behaviour would be similar to `Generic[*Ts]`).

A better name for `TypeConstructor` would prolly be `AritySpec`, short for arity specification, similar to `ParamSpec` (parameter specification).
This should not be subclassable similar to the TypeVarLikes, and type checkers can implement its behaviour.

One problem that arises is how/where do we use bounds here.
`AritySpec` is currently like a variadic `TypeVar` but special cased by type checkers.

A bigger problem that still remains is unsound LSP (Liskov Substitution Principle) when subclassing for constructors.
Should also explore the possibility that intersection types may be required before HKTs.

## Specifying `KindVar`'s with underscore syntax (similar to Scala)

Consider

```python
def fmap[F: Generic[_], A, B](fn: Callable[[A], B], fa: F[A]) -> F[B]: ...
```

OR

```python
def fmap[F[_], A, B](fn: Callable[[A], B], fa: F[A]) -> F[B]: ...
```

In the above cases, `A` and `B` denote a `TypeVar`, while `F` denotes a `KindVar`.

## Misc

Other PEPs/features/interactions to keep in mind as well, although not a top priority, as of now:

- Type variance

- How would the runtime type checker scenario look like?

- PEP 718 – Subscriptable functions

  This PEP is not yet accepted as of now, but could think if there may be any potential clashes here.

- PEP 827 – Type Manipulation

  Also a WIP PEP. Need to look more on this.

Some rough thoughts:

- Would this allow better typing in `functools`, say `functools.singledispatch`?

Possible ways to extend the type system to go towards HKTs:

- Generic `TypeVar` bounds
- Generic metaclasses
- Protocols with `__class_getitem__`
