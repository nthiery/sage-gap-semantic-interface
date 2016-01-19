"""

EXAMPLES::

    sage: G = GAPParent(gap(PermutationGroup([[1,3,2]])))
    sage: G.category()
    Category of finite commutative gap groups
    sage: G.list()
    [(), (2,3)]
    sage: G.random_element()
    ()

    sage: G = GAPParent(gap.FreeMonoid(2))
    sage: G.category()
    Category of infinite gap monoids

    sage: s1, s2 = G.monoid_generators()

    sage: H = GAPParent( G / [ [ s1^2, G.one()], [s2^2, G.one()], [s1*s2*s1, s2*s1*s2]] )
    sage: H.category()
    Category of gap monoids
    sage: H.cardinality()
    6

    sage: t1, t2 = H.monoid_generators()
    sage: t1^2

Mixing and matching Sage and GAP elements::

    sage: C = cartesian_product([G, SymmetricGroup(3)])
    sage: C.category()
    Category of Cartesian products of semigroups

    sage: s1, s2, s3 = G.semigroup_generators()
    sage: s1 * s3 * s2
    s1*s3*s2

    sage: c1,c2 = SymmetricGroup(3).group_generators()
    sage: x = cartesian_product([s1,c1])
    sage: y = cartesian_product([s3,c2])
    sage: x*y
    (s1*s3, (1,3,2))

TODO:
- Choose a good name for the category, in particular in the repr ("gap semigroup" is ambiguous!)
- Keep the handle and the semantic handle separate or together?
- Why does GapElement (which can be e.g. a handle to a group) inherit from RingElement?
- Analogue of an_element in GAP?

"""

from misc.monkey_patch import monkey_patch
from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.structure.element import Element

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

class GAPObject(object):
    def __init__(self, gap_handle):
        self._gap = gap_handle

    def gap(self):
        return self._gap

    def _repr_(self):
        return repr(self.gap())

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
