# HKTs in Scala

This is how Scala handles HKTs currently.

## Examples

```scala
trait Functor[F[_]]:
  def map[A, B](fa: F[A])(f: A => B): F[B]

given Functor[List] with
  def map[A, B](fa: List[A])(f: A => B): List[B] =
    fa.map(f)

// Usage
def transform[F[_], A, B](fa: F[A])(f: A => B)(using F: Functor[F]): F[B] =
  F.map(fa)(f)

@main def run(): Unit =
  val result = transform(List(1, 2, 3))(_ * 2)
  println(result) // List(2, 4, 6)
```

---

- TODO: **Kind polymorphism** via `AnyKind`.

## References

- Scala 3 Kind Polymorphism: https://docs.scala-lang.org/scala3/reference/other-new-features/kind-polymorphism.html
- Adriaan Moors' original papers on higher-kinded generics in Scala.
  - https://adriaanm.github.io/research/2010/10/06/new-in-scala-2.8-type-constructor-inference/
  - https://www.cs.cmu.edu/~aldrich/FOOL/fool08/moors-slides.pdf
- Baeldung – Higher-Kinded Types: https://www.baeldung.com/scala/higher-kinded-types
- Cats library: https://typelevel.org/cats/
