"""

EXAMPLES::

    sage: gap.LoadPackage('"semigroups"')   # If available; needed for some examples below

    sage: from gap_sage import mygap

    sage: G = mygap.Group("(1,2)(3,4)", "(5,6)")
    sage: G.category()
    Category of finite commutative gap groups
    sage: G.list()
    [(), (1,2)(3,4), (5,6), (1,2)(3,4)(5,6)]
    sage: G.an_element()
    ()
    sage: G.random_element() # random
    (5,6)

    sage: M = mygap.FreeMonoid(2)
    sage: M.category()
    Category of infinite gap monoids

    sage: m1, m2 = M.monoid_generators()

Mixing and matching Sage and GAP elements::

    sage: C = cartesian_product([M, ZZ])
    sage: C.category()
    Category of Cartesian products of monoids
    sage: C.an_element()
    (m1, 1)

    sage: x = cartesian_product([m1,3])
    sage: y = cartesian_product([m2,5])
    sage: x*y
    (m1*m2, 15)

Quotient monoids::

    sage: H = M / [ [ m1^2, m1], [m2^2, m2], [m1*m2*m1, m2*m1*m2]]
    sage: H.category()
    Category of gap monoids
    sage: H.is_finite()
    True
    sage: H.cardinality()
    6

Exploring functionalities from the Semigroups package::

    sage: H.is_r_trivial()
    True
    sage: H.is_l_trivial()                   # todo: not implemented in Semigroups; see https://bitbucket.org/james-d-mitchell/semigroups/issues/146/
    True

    sage: classes = H.j_classes(); classes
    [ {m1*m2*m1}, {m2*m1}, {m1}, {m1*m2}, {m2}, {<identity ...>} ]

That's nice::

    sage: classes.category()
    sage: c = classes[0]; c

That's not; we would want this to be a collection::

    sage: c.category()
    Category of elements of [ {m1*m2*m1}, {m2*m1}, {m1}, {m1*m2}, {m2}, {<identity ...>} ]

    sage: pi1, pi2 = H.monoid_generators()
    sage: pi1^2                              # TODO: how to reduce?


Apparently not available for this kind of monoids::

    sage: H.structure_description_schutzenberger_groups()


TODO:
- Choose a good name for the category, in particular in the repr ("gap semigroup" is ambiguous!)
- Keep the handle and the semantic handle separate or together?
- Why does GapElement (which can be e.g. a handle to a group) inherit from RingElement?
  => As a workaround to enable arithmetic and coercion ...
- Would we want to be able to call directly gap methods, as in H.IsJTrivial() ?
"""

from misc.monkey_patch import monkey_patch
from sage.categories.category_with_axiom import all_axioms
from sage.structure.element import Element
from sage.categories.sets_cat import Sets
from sage.categories.unital_algebras import Magmas
from sage.structure.parent import Parent
from sage.interfaces.gap import Gap, gap


import categories
import sage.categories
monkey_patch(categories, sage.categories)

all_axioms += "GAP"

categories_to_categories = {
    "IsMagma": Magmas(),
    "IsMagmaWithOne": Magmas().Unital(),
    "IsMagmaWithInverses": Magmas().Unital().Inverse()
}

true_properties_to_axioms = {
    "IsFinite": "Finite",
    "IsAssociative": "Associative",
    "IsCommutative": "Commutative",
    "IsMonoidAsSemigroup": "Unital",
    "IsGroupAsSemigroup": "Inverse",
}

false_properties_to_axioms = {
    "IsFinite": "Infinite",
}

def GAP(gap_handle):
    if gap_handle.IsCollection():
        return GAPParent(gap_handle)
    else:
        return GAPObject(gap_handle)

class MyGap(Gap):
    def function_call(self, function, args=None, kwds=None):
        # Triggers an infinite recursion, since function_call is used for functions
        # and methods of MyGap objects as well
        # return GAP(super(MyGap, self).function_call(function, args=args, kwds=kwds))
        return GAP(gap.function_call(function, args=args, kwds=kwds))

mygap = MyGap()

class GAPObject(object):
    def __init__(self, gap_handle):
        self._gap = gap_handle

    def gap(self):
        return self._gap

    def _repr_(self):
        return repr(self.gap())

    def _wrap(self, obj):
        return GAP(obj)

class GAPParent(GAPObject, Parent):
    def __init__(self, gap_handle):
        category = Sets()
        for cat in gap_handle.CategoriesOfObject():
            cat = str(cat)
            if cat in categories_to_categories:
                category = category & categories_to_categories[cat]
        properties = set(str(prop) for prop in gap_handle.KnownPropertiesOfObject())
        true_properties = set(str(prop) for prop in gap_handle.KnownTruePropertiesOfObject())
        for prop in properties:
            if prop in true_properties:
                if prop in true_properties_to_axioms:
                    category = category._with_axiom(true_properties_to_axioms[prop])
            else:
                if prop in false_properties_to_axioms:
                    category = category._with_axiom(false_properties_to_axioms[prop])
        Parent.__init__(self, category=category.GAP())
        GAPObject.__init__(self, gap_handle)

    def _element_constructor(self, gap_handle):
        assert isinstance(gap_handle, sage.interfaces.gap.GapElement)
        return self.element_class(self, gap_handle)

    def gap(self):
        return self._gap

    class Element(GAPObject, Element):
        def __init__(self, parent, gap_handle):
            Element.__init__(self, parent)
            GAPObject.__init__(self, gap_handle)
