from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method
from sage.libs.gap.libgap import libgap

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
                    sage: F = mygap.FreeGroup("a", "b")
                    sage: a, b = F.group_generators()
                    sage: G = F / [ a * b * a^-1 * b^-1 ]
                    sage: G
                    <fp group of size infinity on the generators [ a, b ]>
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
                    <fp group of size infinity on the generators [ a, b ]>
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
                return self._wrap( self.gap() / libgap([x.gap() for x in relators]) )
