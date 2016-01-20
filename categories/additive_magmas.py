r"""
Handles for GAP additive magmas
"""
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.misc.cachefunc import cached_method

class AdditiveMagmas:

    class GAP(CategoryWithAxiom):

        class ElementMethods:

            def _add_(self, other):
                r"""
                Return the sum of self and other

                EXAMPLES::

                    sage: sys.path.insert(0, "./")
                    sage: from gap_sage import mygap
                    sage: P = mygap.eval("PositiveIntegers")
                    sage: a = P.an_element()
                    sage: a
                    1
                    sage: a + a
                    2
                """
                return self.parent(self.gap() + other.gap()) # TODO; call directly the gap operation

    class AdditiveUnital(CategoryWithAxiom):

        class GAP(CategoryWithAxiom):

            class ParentMethods:

                @cached_method
                def zero(self):
                    r"""
                    Return the zero element of this additive magma with zero.

                    EXAMPLE::

                        sage: sys.path.insert(0, "./")
                        sage: from gap_sage import mygap
                        sage: N = mygap.eval("Integers"); N
                        Integers
                        sage: N.zero()
                        0
                        sage: P = mygap.eval("PositiveIntegers"); P
                        PositiveIntegers
                        sage: P.zero()
                        Traceback (most recent call last):
                        ...
                        AttributeError: 'GAPParent_with_category' object has no attribute 'zero'

                    """
                    return self(self.gap().Zero())
