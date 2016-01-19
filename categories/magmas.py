from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method

class Magmas:
    class GAP(CategoryWithAxiom):

        class ElementMethods:

            def _mul_(self, other):
                r"""
                Return the product of self by other

                EXAMPLES::

                    sage: G = GAPParent(gap.FreeSemigroup(3))
                    sage: s1, s2, s3 = G.semigroup_generators()
                    sage: s1 * s3 * s2
                    s1*s3*s2
                """
                return self.parent(self.gap() * other.gap()) # TODO; call directly the gap operation

    class Unital(CategoryWithAxiom):
        class GAP(CategoryWithAxiom):
            class ParentMethods:
                def one(self):
                    return self(self.gap().One())
