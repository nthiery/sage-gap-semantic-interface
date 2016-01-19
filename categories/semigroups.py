from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.misc.cachefunc import cached_method
from sage.interfaces.gap import gap

class Semigroups:
    class GAP(CategoryWithAxiom):

        class ParentMethods:

            @cached_method
            def semigroup_generators(self):
                r"""
                Return generators for this semigroup.

                OUTPUT:

                    A tuple of elements of ``self``

                EXAMPLES::

                    sage: SL(1, 17).is_abelian()
                    True
                    sage: SL(2, 17).is_abelian()
                    False
                """
                return tuple(self(handle) for handle in self.gap().GeneratorsOfSemigroup())

            def __div__(self, relations):
                return self.gap() / gap([[x.gap(), y.gap()] for x,y in relations])

    class Unital:
        class GAP(CategoryWithAxiom):
            class ParentMethods:
                @cached_method
                def monoid_generators(self):
                    r"""
                    Return generators for this monoid

                    OUTPUT:

                        A tuple of elements of ``self``

                    EXAMPLES::

                        sage: SL(1, 17).is_abelian()
                        True
                        sage: SL(2, 17).is_abelian()
                        False
                    """
                    return tuple(self(handle) for handle in self.gap().GeneratorsOfMonoid())

