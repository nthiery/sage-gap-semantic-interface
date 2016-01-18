from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms

class FiniteGroups:
    class GAP(CategoryWithAxiom):

        class ParentMethods:
            def list(self):
                return self.gap().List()
