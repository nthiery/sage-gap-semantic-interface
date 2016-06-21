r"""
Handles for GAP Lie algebras

EXAMPLES:

Create a Lie algebra::

    sage: from mygap import mygap
    sage: a, b = matrix(ZZ, 2, [0, 1, 0, 0]), matrix(ZZ, 2, [0, 0, 1, 0])
    sage: L = mygap.LieAlgebra( QQ, [a, b] )
    sage: L
    <Lie algebra over Rationals, with 2 generators>

Check the category of our gap Lie algebra::

    sage: L.category()
    Category of g a p lie algebras over rings

Compute the Lie bracket::

    sage: a, b = L.lie_algebra_generators()
    sage: a * a
    LieObject( [ [ 0, 0 ],
                 [ 0, 0 ] ] )
    sage: a * b
    LieObject( [ [ 1, 0 ],
                 [ 0, -1 ] ] )

Check membership::

    sage: a * b in L
    True


.. TODO::

    - For now, we are denoting Lie bracket as multiplication as in GAP.
      (For the case of Lie algebras defined from an associative algebra by
      taking commutators for the Lie bracket, GAP wraps Lie algebra elements
      using `LieObject`.)
      Later we might want to make things compatible with Travis Scrimshaw's
      bracket notation in his work on Lie algebras at :trac:`14901`.
"""
from sage.categories.category_types import Category_over_base_ring
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.magmatic_algebras import MagmaticAlgebras
from sage.misc.cachefunc import cached_method
from sage.interfaces.gap import gap

class LieAlgebras(Category_over_base_ring):

    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: from categories.lie_algebras import LieAlgebras
            sage: LieAlgebras(Rings()).super_categories()
            [Category of magmatic algebras over rings]
        """
        return [MagmaticAlgebras(self.base_ring())]

    class GAP(CategoryWithAxiom):

        def example(self):
            r"""
            Return an example of Lie algebra.

            EXAMPLE::

                sage: from categories.lie_algebras import LieAlgebras
                sage: LieAlgebras(Rings()).GAP().example()
                <Lie algebra over Rationals, with 2 generators>
            """
            from mygap import mygap
            from sage.matrix.constructor import matrix
            from sage.rings.rational_field import QQ
            a = matrix([[0, 1],
                        [0, 0]])
            b = matrix([[0, 0],
                        [1, 0]])
            return mygap.LieAlgebra( QQ, [a, b] )

        class ParentMethods:

            @cached_method
            def lie_algebra_generators(self):
                r"""
                Return generators for this Lie algebra.

                OUTPUT:

                    A tuple of elements of ``self``

                EXAMPLES::

                    sage: from categories.lie_algebras import LieAlgebras
                    sage: L = LieAlgebras(Rings()).GAP().example()
                    sage: a, b = L.lie_algebra_generators()
                    sage: a, b
                    (LieObject( [ [ 0, 1 ],
                                  [ 0, 0 ] ] ),
                     LieObject( [ [ 0, 0 ],
                                  [ 1, 0 ] ] ))
                """
                return tuple(self(handle) for handle in self.gap().GeneratorsOfAlgebra())

        class ElementMethods:

            pass

