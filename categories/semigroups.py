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

            def __truediv__(self, relations):
                return self._wrap( self.gap() / gap([[x.gap(), y.gap()] for x,y in relations]) )

            def is_l_trivial(self):
                return self.gap().IsLTrivial().sage()

            def is_r_trivial(self):
                return self.gap().IsRTrivial().sage()

            def is_d_trivial(self):
                return self.gap().IsDTrivial().sage()

            def j_classes(self):
                return self._wrap(self.gap().JClasses())

            def l_classes(self):
                return self._wrap(self.gap().LClasses())

            def r_classes(self):
                return self._wrap(self.gap().RClasses())

            def structure_description_maximal_subgroups(self):
                return self._wrap(self.gap().StructureDescriptionMaximalSubgroups())

            def structure_description_schutzenberger_groups(self):
                return self._wrap(self.gap().StructureDescriptionSchutzenbergerGroups())

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

