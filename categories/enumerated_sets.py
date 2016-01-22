import itertools
from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms

class EnumeratedSets:
    class GAP(CategoryWithAxiom):
        class ParentMethods:
            def __iter__(self):
                """
                EXAMPLES::

                    sage: sys.path.insert(0, "./")
                    sage: from mygap import mygap
                    sage: F = mygap.FiniteField(3)
                    sage: for x in F: # indirect doctest
                    ....:     print x
                    0*Z(3)
                    Z(3)^0
                    Z(3)

                    sage: for x in F: # indirect doctest
                    ....:     assert x.parent() is F
                """
                return itertools.imap(self, self._wrap(self.gap().Iterator()))
