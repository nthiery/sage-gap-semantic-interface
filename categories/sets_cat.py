from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method

all_axioms += ("GAP",)

class Sets:

    class SubcategoryMethods:

        @cached_method
        def GAP(self):
            """
            Return the full subcategory of the objects of ``self`` represented by a handle to a GAP object.

            EXAMPLES::

                sage: Sets().GAP()

            TESTS::

                sage: TestSuite(Sets().GAP()).run()
                sage: Groups().GAP.__module__
                'sage.categories.sets_cat'
            """
            return self._with_axiom('GAP')

    class GAP(CategoryWithAxiom):
        class ParentMethods:

            def is_finite(self):
                return self.gap().IsFinite().sage()

            def cardinality(self):
                return self.gap().Size().sage()

            def _an_element_(self):
                """
                Return an element of this set.

                EXAMPLES::

                    sage: 
                """
                return self(self.gap().Representative())

            def random_element(self):
                """
                Return a random element of this set.

                OUTPUT:

                A group element.

                EXAMPLES::

                    sage: G = Sp(4,GF(3))
                    sage: G.random_element()  # random
                    [2 1 1 1]
                    [1 0 2 1]
                    [0 1 1 0]
                    [1 0 0 1]
                    sage: G.random_element() in G
                    True

                    sage: F = GF(5); MS = MatrixSpace(F,2,2)
                    sage: gens = [MS([[1,2],[-1,1]]),MS([[1,1],[0,1]])]
                    sage: G = MatrixGroup(gens)
                    sage: G.random_element()  # random
                    [1 3]
                    [0 3]
                    sage: G.random_element() in G
                    True
                """
                return self(self.gap().Random())


    class Finite:
        class GAP(CategoryWithAxiom):
            class ParentMethods:
                def list(self):
                    return [self(handle) for handle in self.gap().List()]
