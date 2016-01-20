from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method
from sage.interfaces.gap import gap

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

            def __truediv__(self, relators):
                r"""
                Return the quotient group of self by list of relations or relators

                TODO:

                - also accept list of relations as couples of elements,
                  like semigroup quotients do.

                EXAMPLES:

                We define `ZZ^2` as a quotient of the free group
                on two generators::

                    sage: sys.path.insert(0, "./")
                    sage: from gap_sage import mygap
                    sage: F = mygap.FreeGroup( '"a"', '"b"' )
                    sage: a, b = F.group_generators()
                    sage: G = F / [ a * b * a^-1 * b^-1 ]
                    sage: G
                    Group( [ a, b ] )
                    sage: a, b = G.group_generators()
                    sage: a * b * a^-1 * b^-1
                    a*b*a^-1*b^-1

                Here, equality testing works well::

                    sage: a * b * a^-1 * b^-1 == G.one()
                    True

                We define a Baumslag-Solitar group::

                    sage: a, b = F.group_generators()
                    sage: G = F / [ a * b * a^-1 * b^-2 ]
                    sage: G
                    Group( [ a, b ] )
                    sage: a, b = G.group_generators()
                    sage: a * b * a^-1 * b^-2
                    a*b*a^-1*b^-2

                Here, equality testing starts an infinite loop where GAP is trying
                to make the rewriting system confluent (a better implementation
                would alternate between making the rewriting system more confluent
                and trying to answer the equality question -- this is a known
                limitation of GAP's implementation of the Knuth-Bendix procedure)::

                    sage: a * b * a^-1 * b^-2 == G.one() # not tested
                """
                return self._wrap( self.gap() / gap([x.gap() for x in relators]) )

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

