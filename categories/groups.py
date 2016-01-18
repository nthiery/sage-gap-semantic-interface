from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method

class Groups:
    class GAP(CategoryWithAxiom):

        class ParentMethods:
            @cached_method
            def is_abelian(self):
                r"""
                Test whether the group is Abelian.

                OUTPUT:

                Boolean. ``True`` if this group is an Abelian group.

                EXAMPLES::

                    sage: SL(1, 17).is_abelian()
                    True
                    sage: SL(2, 17).is_abelian()
                    False
                """
                return self.gap().IsAbelian().sage()
