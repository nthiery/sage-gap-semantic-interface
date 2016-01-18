"""

EXAMPLES::

    sage: G = GAPParent(gap(PermutationGroup([[1,3,2]])), Groups().Finite())
"""

from sage.misc.bindable_class import BindableClass
from monkey_patch import MonkeyPatch

#G = Groups().Finite()
#G.GAP=ConstantFunction(G)

#class Groups:
#    class Finite:
 #       pass

Groups.Finite

class _(MonkeyPatch, Groups):
    class Finite:

        class GAP(Category):
            def super_categories(self):
                return [Groups().Finite()]

            class ParentMethods:
                def list(self):
                    return self.gap().List()

class GAPParent(Parent):
    def __init__(self, gap_handle, category):
        # TODO: category discovery from the gap handle
        Parent.__init__(self, category=category.GAP())
        self._gap = gap_handle

    def gap(self):
        return self._gap
