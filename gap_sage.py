"""

EXAMPLES::

    sage: G = GAPParent(gap(PermutationGroup([[1,3,2]])), Groups().Finite())
"""

from misc.monkey_patch import monkey_patch
import categories
import sage.categories
from sage.structure.element import Element
monkey_patch(categories, sage.categories)

#G = Groups().Finite()
#G.GAP=ConstantFunction(G)

#class Groups:
#    class Finite:
 #       pass

from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms

all_axioms += "GAP"


#Sets().subcategory_class.GAP = Sets.SubcategoryMethods.__dict__["GAP"]


# Groups.Finite
# class _(MonkeyPatch, Groups):
#     class Finite:

#         class GAP(CategoryWithAxiom):

#             _base_category_class_and_axiom = (Groups.Finite, "GAP")

#             class ParentMethods:
#                 def list(self):
#                     return self.gap().List()

class GAPObject(object):
    def __init__(self, gap_handle):
        self._gap = gap_handle

    def gap(self):
        return self._gap

    def _repr_(self):
        return repr(self.gap())

    def _element_constructor(self, gap_handle):
        assert isinstance(gap_handle, sage.interfaces.gap.GapElement)
        return self.element_class(self, gap_handle)

class GAPParent(Parent, GAPObject):
    def __init__(self, gap_handle, category):
        # TODO: category discovery from the gap handle
        Parent.__init__(self, category=category.GAP())
        GAPObject.__init__(self, gap_handle)

    def gap(self):
        return self._gap

    class Element(GAPObject, Element):
        def __init__(self, parent, gap_handle):
            Element.__init__(self, parent)
            GAPObject.__init__(self, gap_handle)
