from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method

all_axioms += ("GAP",)

class Objects:

    class SubcategoryMethods:

        @cached_method
        def GAP(self):
            """
            Return the full subcategory of the objects of ``self`` represented by a handle to a GAP object.

            EXAMPLES::

                sage: from mygap import mygap
                sage: from sage.categories.sets_cat import Sets

                sage: Sets().GAP()
                Category of g a p sets

            TESTS::

                sage: TestSuite(Sets().GAP()).run()
                sage: Groups().GAP.__module__
                'categories.objects'
            """
            return self._with_axiom('GAP')

    class GAP(CategoryWithAxiom):
        pass
