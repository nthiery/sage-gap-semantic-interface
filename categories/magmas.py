from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method

class Magmas:
    class GAP(CategoryWithAxiom):

        class ElementMethods:

            def _mul_(self, other):
                r"""
                Return the product of self by other

                EXAMPLES::

                    sage: sys.path.insert(0, "./")
                    sage: from gap_sage import mygap
                    sage: G = mygap.FreeSemigroup(3)
                    sage: s1, s2, s3 = G.semigroup_generators()
                    sage: s1 * s3 * s2
                    s1*s3*s2
                """
                return self.parent(self.gap() * other.gap()) # TODO; call directly the gap operation

    class Unital:
        class GAP(CategoryWithAxiom):
            class ParentMethods:
                def one(self):
                    return self(self.gap().One())

            class ElementMethods:
                def __invert__(self):
                    r"""
                    Return the inverse of this element.

                    EXAMPLES::

                        sage: sys.path.insert(0, "./")
                        sage: from gap_sage import mygap
                        sage: G = mygap.FreeGroup("a")
                        sage: a, = G.group_generators()
                        sage: a.__invert__()
                        a^-1
                        sage: a^-1
                        a^-1
                        sage: ~a
                        a^-1
                        sage: ~a * a
                        <identity ...>

                    This also works when the inverse is only partially defined::

                        sage: F = mygap.FiniteField(3)
                        sage: a = F.one(); a
                        Z(3)^0
                        sage: ~a
                        Z(3)^0
                        sage: ~(a+a)
                        Z(3)
                        sage: a = F.zero()
                        sage: ~a
                        Traceback (most recent call last):
                        ...
                        ValueError: 0*Z(3) is not invertible
                    """
                    from sage.libs.gap.libgap import libgap
                    fail = libgap.eval("fail")
                    inverse = self.gap().Inverse()
                    if inverse == fail:
                        raise ValueError("%s is not invertible"%self)
                    return self.parent()(inverse)
