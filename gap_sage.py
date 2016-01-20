"""
EXAMPLES::

    sage: gap.LoadPackage('"semigroups"')    # Needed for some examples below
    true

    sage: from gap_sage import mygap

    sage: G = mygap.Group("(1,2)(3,4)", "(5,6)")
    sage: G.category()
    Category of finite gap groups
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

    sage: H._refine_category_()
    sage: H.category()
    Category of finite gap monoids

    sage: H.list()
    [<identity ...>, m1, m2, m1*m2, m2*m1, m1*m2*m1]

The following do not work because the elements don't have a normal
form. We would need to have the monoid elements represented in normal
form, or the hash function to compute first a normal form::

    sage: C = H.cayley_graph()
    sage: len(C.vertices())    # expecting 6
    13
    sage: len(C.edges())
    12

    sage: phi = H.isomorphism_transformation_monoid()
    sage: phi.domain() == H    # is?
    True
    sage: HH = phi.codomain(); HH
    Monoid( [ Transformation( [ 2, 2, 5, 6, 5, 6 ] ),
              Transformation( [ 3, 4, 3, 4, 6, 6 ] ) ] )

    sage: C = HH.cayley_graph()
    sage: C.vertices()                         # random
    [Transformation( [ 2, 2, 5, 6, 5, 6 ] ),
     Transformation( [ 3, 4, 3, 4, 6, 6 ] ),
     IdentityTransformation,
     Transformation( [ 4, 4, 6, 6, 6, 6 ] ),
     Transformation( [ 5, 6, 5, 6, 6, 6 ] ),
     Transformation( [ 6, 6, 6, 6, 6, 6 ] )]
    sage: len(C.edges())
    12

    sage: C.relabel(phi.preimage)
    sage: sorted(C.vertices(), key=str)
    [<identity ...>, m1, m1*m2, m1*m2*m1, m2, m2*m1]
    sage: sorted(C.edges(),    key=str)
    [(<identity ...>, m1, Transformation( [ 2, 2, 5, 6, 5, 6 ] )),
     (<identity ...>, m2, Transformation( [ 3, 4, 3, 4, 6, 6 ] )),
     (m1*m2*m1, m1*m2*m1, Transformation( [ 2, 2, 5, 6, 5, 6 ] )),
     (m1*m2*m1, m1*m2*m1, Transformation( [ 3, 4, 3, 4, 6, 6 ] )),
     (m1*m2, m1*m2*m1, Transformation( [ 2, 2, 5, 6, 5, 6 ] )),
     (m1*m2, m1*m2, Transformation( [ 3, 4, 3, 4, 6, 6 ] )),
     (m1, m1*m2, Transformation( [ 3, 4, 3, 4, 6, 6 ] )),
     (m1, m1, Transformation( [ 2, 2, 5, 6, 5, 6 ] )),
     (m2*m1, m1*m2*m1, Transformation( [ 3, 4, 3, 4, 6, 6 ] )),
     (m2*m1, m2*m1, Transformation( [ 2, 2, 5, 6, 5, 6 ] )),
     (m2, m2*m1, Transformation( [ 2, 2, 5, 6, 5, 6 ] )),
     (m2, m2, Transformation( [ 3, 4, 3, 4, 6, 6 ] ))]

Exploring functionalities from the Semigroups package::

    sage: H.is_r_trivial()
    True
    sage: H.is_l_trivial()                   # todo: not implemented in Semigroups; see https://bitbucket.org/james-d-mitchell/semigroups/issues/146/
    True

    sage: classes = H.j_classes(); classes
    [ {m1*m2*m1}, {m2*m1}, {m1}, {m1*m2}, {m2}, {<identity ...>} ]

That's nice::

    sage: classes.category()
    Category of finite gap sets
    sage: c = classes[0]; c
    {m1*m2*m1}

That's not; we would want this to be a collection::

    sage: c.category()
    Category of elements of [ {m1*m2*m1}, {m2*m1}, {m1}, {m1*m2}, {m2}, {<identity ...>} ]

    sage: pi1, pi2 = H.monoid_generators()
    sage: pi1^2 == pi1
    True

Apparently not available for this kind of monoids::

    sage: H.structure_description_schutzenberger_groups() # todo: not implemented


TODO:
- Choose a good name for the category, in particular in the repr ("gap semigroup" is ambiguous!)
- Keep the handle and the semantic handle separate or together?
- Why does GapElement (which can be e.g. a handle to a group) inherit from RingElement?
  => As a workaround to enable arithmetic and coercion ...
- Would we want to be able to call directly gap methods, as in H.IsJTrivial() ?

- Tracing mode allowing for reproducing the sequence of GAP
  instructions corresponding to a sequence of Sage instructions
"""

import sys
sys.path.insert(0, "./")          # TODO

from misc.monkey_patch import monkey_patch
from sage.categories.category_with_axiom import all_axioms
from sage.structure.element import Element
from categories.lie_algebras import LieAlgebras
from sage.categories.rings import Rings
from sage.categories.sets_cat import Sets
from sage.categories.unital_algebras import Magmas
from sage.structure.parent import Parent
from sage.interfaces.gap import Gap, gap, GapElement
from sage.misc.cachefunc import cached_method

import categories
import sage.categories
monkey_patch(categories, sage.categories)

all_axioms += "GAP"

categories_to_categories = {
    "IsMagma": Magmas(),
    "IsMagmaWithOne": Magmas().Unital(),
    "IsMagmaWithInverses": Magmas().Unital().Inverse(),
}

true_properties_to_axioms = {
    "IsFinite": "Finite",
    "IsAssociative": "Associative",
    "IsCommutative": "Commutative",
    "IsMonoidAsSemigroup": "Unital",
    "IsGroupAsSemigroup": "Inverse",
    # GAP's IsLieAlgebra is a filter to several properties,
    # IsAlgebra, IsZeroSquareRing, and IsJacobianRing
    "IsJacobianRing": LieAlgebras(Rings())
}

false_properties_to_axioms = {
    "IsFinite": "Infinite",
}

def retrieve_category_of_gap_handle(self):
    category = Sets()
    for cat in self.CategoriesOfObject():
        cat = str(cat)
        if cat in categories_to_categories:
            category = category & categories_to_categories[cat]
    properties = set(str(prop) for prop in self.KnownPropertiesOfObject())
    true_properties = set(str(prop) for prop in self.KnownTruePropertiesOfObject())
    for prop in properties:
        if prop in true_properties:
            if prop in true_properties_to_axioms:
                axiom = true_properties_to_axioms[prop]
                if isinstance(axiom, str):
                    category = category._with_axiom(axiom)
                else:
                    category = category & axiom
        else:
            if prop in false_properties_to_axioms:
                category = category._with_axiom(false_properties_to_axioms[prop])
    return category

GapElement.retrieve_category = retrieve_category_of_gap_handle

def GAP(gap_handle):
    if gap_handle.IsCollection():
        return GAPParent(gap_handle)
    elif gap_handle.IsMapping():
        return GAPMorphism(gap_handle)
    else:
        return GAPObject(gap_handle)

sage.interfaces.gap.trace = False

class MyGap(Gap):
    def function_call(self, function, args=None, kwds=None):
        # Triggers an infinite recursion, since function_call is used for functions
        # and methods of MyGap objects as well
        # return GAP(super(MyGap, self).function_call(function, args=args, kwds=kwds))

        if sage.interfaces.gap.trace:
            print "%s(%s)"%(function, ','.join(x if isinstance(x, str) else x._name for x in args))

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

    @cached_method
    def __hash__(self):
        return hash(self._repr_())

    def __cmp__(self, other):
        return cmp(id(self), id(other))

    def __eq__(self, other):
        """
        Return whether ``self`` and ``other`` are equal.

        EXAMPLES::

            sage: M = mygap.FreeMonoid(2)
            sage: M.category()
            Category of infinite gap monoids
            sage: m1, m2 = M.monoid_generators()
            sage: m1 == m1
            True
            sage: m1 == m2
            False
            sage: m1*m2 == m2*m1
            False
            sage: m1*m2 == m1*m2
            True

            sage: H = M / [ [ m1^2, m1], [m2^2, m2], [m1*m2*m1, m2*m1*m2]]
            sage: pi1, pi2 = H.monoid_generators()
            sage: pi1^2 == pi1
            True
            sage: pi1*pi2*pi1 == pi2*pi1*pi2
            True

        TESTS::

            sage: M == M
            True
            sage: M == mygap.FreeMonoid(2)
            False
            sage: M == 0
            False
        """
        return self.__class__ is other.__class__ and bool(self.gap().EQ(other.gap()))

    def __ne__(self, other):
        return not self == other

class GAPParent(GAPObject, Parent):
    def __init__(self, gap_handle):
        Parent.__init__(self, category=gap_handle.retrieve_category().GAP())
        GAPObject.__init__(self, gap_handle)

    def _element_constructor(self, gap_handle):
        assert isinstance(gap_handle, sage.interfaces.gap.GapElement)
        return self.element_class(self, gap_handle)

    def gap(self):
        return self._gap

    def _refine_category_(self, category=None):
        if category is None:
            category = self.gap().retrieve_category().GAP()
        super(GAPParent, self)._refine_category_(category)

    class Element(GAPObject, Element):
        def __init__(self, parent, gap_handle):
            Element.__init__(self, parent)
            GAPObject.__init__(self, gap_handle)

class GAPMorphism(GAPObject): # TODO: inherit from morphism and move the methods to the categories
    @cached_method
    def domain(self):
        return self._wrap(self.gap().Source())

    @cached_method
    def codomain(self):
        return self._wrap(self.gap().Range())

    def __call__(self, x):
        return self.codomain()(self.gap().ImageElm(x.gap()))

    def preimage(self, y):
        return self.domain()(self.gap().PreImageElm(y.gap()))
