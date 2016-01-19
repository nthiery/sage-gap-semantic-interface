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

            @cached_method
            def group_generators(self):
                r"""
                Return generators for this group.

                OUTPUT:

                    A tuple of elements of ``self``

                EXAMPLES::

                    sage: SL(1, 17).is_abelian()
                    True
                    sage: SL(2, 17).is_abelian()
                    False
                """
                return tuple(self(handle) for handle in self.gap().GeneratorsOfGroup())

        class ElementMethods:

            def __invert__(self):
                r"""
                Return the inverse of this element.

                EXAMPLES::

                    sage: sys.path.insert(0, "./")
                    sage: from gap_sage import mygap
                    sage: G = mygap.FreeGroup('"a"')
                    sage: a, = G.group_generators()
                    sage: a.__invert__()
                    a^-1
                    sage: a^-1
                    a^-1
                    sage: ~a
                    a^-1
                    sage: ~a * a
                    <identity ...>
                """
                return self.parent()(self.gap().Inverse())

