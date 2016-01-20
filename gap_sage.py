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


TODO and design discussions
===========================

Vocabulary
----------

- "semantic handle" versus "handle" versus ???

User interface and features
---------------------------

- Keep the handle and the semantic handle separate or together?
- For a Sage object, what should .gap() return: a plain handle or a semantic handle
- Make it easy for the user to discover GAP methods and access documentation
  By tab completion?
  On the object itself or on some attribute of it?

       H.IsFinite   /   H.gap.IsFinite   /   H.gap().IsFinite()

  Should the method call return a plain gap handle or a semantic one?
  Would we want to be able to call directly gap methods, as in H.IsJTrivial() ?
- In general, do we want to hide the non semantic handles?

- Accessing objects (and not just functions) from the global namespace of gap

  For example, the "Cyclotomics" is a GAP object, not a
  function. Currently one needs to do::

      sage: libgap.eval("Cyclotomics")
      Cyclotomics

  Would we want instead::

      sage: gap.eval("Cyclotomics")        # todo: not tested
      Cyclotomics

About the category-based approach
---------------------------------

- Pros: very little infrastructure; infrastructure that can be easily
  reused by other parents / ...

- Issue: because the GAP interface mixins are part of the category
  hierarchy, there can be ambiguity (how often?) between using an
  existing generic implementation in Sage and using the GAP interface.

  Example: (TODO)

- Choose a good name for the categories:

  - Semigroups().GAP()
  - Semigroups()._GAP()

  And for their repr:

  - Category of gap semigroups (ambiguous: semigroups having a gap?)
  - Category of semigroups implemented in GAP (long)
  - Category of GAP semigroups

Source code organization
------------------------

- Separate file / folder with monkey patching of the main Sage categories?
  This makes it handy for automatic generation / maintenance
- Issue: Some duplication in the nested classes requires consistency
  betwen nested classes of the main categories and the nested classes
  here
- Issue: How to support lazy import?

libGAP
------

- Feature: Tracing mode allowing for reproducing the sequence of GAP
  instructions corresponding to a sequence of Sage instructions::

     sage: libgap.log(True)                   # todo: not implemented
     sage: G = mygap.SymmetricGroup(3)
     sage: G.list()
     [(), (1,3), (1,2,3), (2,3), (1,3,2), (1,2)]

     sage: print libgap.get_log()             # todo: not implemented
     $sage1 := SymmetricGroup(3);
     Size($sage1)

  Applications:
  - Debugging the interface
  - Learning how to do the same computation in GAP

  - In case of issue/limitation/..., being able to test if the problem
    is in the interface or in GAP, and in the later case to send a
    plain GAP scenario to the GAP devs

- Method(s) for calling a GAP function (given by a name) or operator
  (given by a string, like "*") on a bunch of handles::

      libgap.call("Size", gap_handle)
      libgap.call("+", gap_handle, gap_handle)

- Renable Tab completion in "gap" object
- Handling of strings as arguments to functions / methods. The following
  is a bit of a pain:

      sage: gap.FreeGroup('"a"', '"b"')
      Group( [ a, b ] )

  I'd rather have GAP string evaluation being done explicitly:

      sage: gap.FreeGroup("a", "b")        # not tested

      sage: gap.eval("a")                  # not tested

  Is there a path for this without breaking backward compatibility?

- Why does GapElement (which can be e.g. a handle to a group) inherit from RingElement?
  => As a workaround to enable arithmetic and coercion ...

Misc TODO
---------

- Merge gap / mygap
- Merging the code into Sage
"""

import sys
sys.path.insert(0, "./")          # TODO

from misc.monkey_patch import monkey_patch
from sage.categories.category_with_axiom import all_axioms
from sage.structure.element import Element
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
                category = category._with_axiom(true_properties_to_axioms[prop])
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
        return self != other

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
