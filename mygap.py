"""
"Semantic aware" Sage interface to GAP

This module, built on top of libgap, enriches the handles to GAP
objects by retrieving their mathematical properties from GAP, and
exposing them to Sage, to make them behave as native Sage objects.

EXAMPLES:

Some initialization::

    sage: libgap.LoadPackage("semigroups")    # optional - semigroups
    #I  method installed for Matrix matches more than one declaration
    true

    sage: from mygap import mygap

Let's construct a handle to a GAP permutation group::

    sage: G = mygap.Group(libgap.eval("[(1,2)(3,4), (5,6)]"))

This "semantic" handle is automatically recognized as a finite Sage group::

    sage: G in Groups().Finite()
    True

and behaves as such::

    sage: G.list()
    [(), (1,2)(3,4), (5,6), (1,2)(3,4)(5,6)]
    sage: G.an_element()
    ()
    sage: G.random_element() # random
    (5,6)
    sage: s, t = G.group_generators()
    sage: s * t
    (1,2)(3,4)(5,6)

This handle is actually in the "category of GAP groups"::

    sage: G.category()
    Category of finite g a p groups

This category, together with its super categories of "GAP monoids",
"GAP magmas", etc, provide wrapper methods that translate the Sage
method calls to the corresponding GAP function calls.

Doing this using a hierarchy of categories allow to implement, for
example, once for all the wrapper method for multiplication (_mul_ ->
Prod) for all multiplicative structures in Sage.

Let's now consider a monoid::

    sage: M = mygap.FreeMonoid(2)
    sage: M.category()
    Category of infinite g a p monoids

    sage: m1, m2 = M.monoid_generators()
    sage: m1 * m2 * m1 * m2
    (m1*m2)^2

We can now mix and match Sage and GAP elements::

    sage: C = cartesian_product([M, ZZ])
    sage: C.category()
    Category of Cartesian products of monoids
    sage: C.an_element()               # optional - semigroups
    (m1, 1)

    sage: x = cartesian_product([m1,3])
    sage: y = cartesian_product([m2,5])
    sage: x*y
    (m1*m2, 15)

Here is a quotient monoid::

    sage: H = M / [ [ m1^2, m1], [m2^2, m2], [m1*m2*m1, m2*m1*m2]]
    sage: H.category()
    Category of g a p monoids
    sage: H.is_finite()
    True
    sage: H.cardinality()
    6

    sage: H._refine_category_()
    sage: H.category()
    Category of finite g a p monoids

    sage: H.list()
    [<identity ...>, m1, m2, m1*m2, m2*m1, m1*m2*m1]

Building the Cayley graph does not work because the elements don't
have a normal form. We would need to have the monoid elements
represented in normal form, or the hash function to compute first a
normal form. This problem is not specific to the Sage-GAP interface::

    sage: C = H.cayley_graph()
    sage: len(C.vertices())    # expecting 6
    13
    sage: len(C.edges())
    12

So we build the Cayley graph from an isomorphic monoid having a normal
form; this is the occasion to showcase the use of a GAP morphism::

    sage: phi = H.isomorphism_transformation_monoid()
    sage: phi.domain() == H    # is?
    True
    sage: HH = phi.codomain(); HH
    <transformation monoid of size 6, degree 6 with 2 generators>

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
    [(<identity ...>, m1, 0),
      (<identity ...>, m2, 1),
      (m1*m2*m1, m1*m2*m1, 0),
      (m1*m2*m1, m1*m2*m1, 1),
      (m1*m2, m1*m2*m1, 0),
      (m1*m2, m1*m2, 1),
      (m1, m1*m2, 1),
      (m1, m1, 0),
      (m2*m1, m1*m2*m1, 1),
      (m2*m1, m2*m1, 0),
      (m2, m2*m1, 0),
      (m2, m2, 1)]

More examples of structure computations with finite semigroups::

    sage: T = mygap.FullTransformationMonoid(4)

    sage: T.structure_description_maximal_subgroups() # optional - semigroups
    [ "1", "C2", "S3", "S4" ]

    sage: T.j_classes()
    [ <Green's D-class: Transformation( [ 1, 1, 1, 1 ] )>,
      <Green's D-class: Transformation( [ 1, 1, 1, 2 ] )>,
      <Green's D-class: Transformation( [ 1, 1, 2, 3 ] )>,
      <Green's D-class: IdentityTransformation> ]

    sage: R = T.r_classes()
    sage: R
    [ <Green's R-class: Transformation( [ 1, 1, 1, 1 ] )>,
      ...
      <Green's R-class: IdentityTransformation> ]

    sage: C = R[11]; C
    <Green's R-class: Transformation( [ 1, 2, 3, 1 ] )>
    sage: C.category()
    Category of facade finite g a p greens class
    sage: C.cardinality()
    24
    sage: C.schutzenberger_group()      # optional - semigroups
    Group([ (1,2,3), (1,2) ])

    sage: C[0]
    Transformation( [ 1, 2, 3, 1 ] )
    sage: C[0].parent()
    <full transformation monoid of degree 4>


Let's construct a variety of GAP parents to check that they pass all
the generic tests; this means that they have a chance to behave
reasonably as native Sage parents::

    sage: skip = ["_test_pickling", "_test_elements"] # Pickling fails for now

    sage: F = mygap.eval("Cyclotomics"); F
    Cyclotomics
    sage: F in Fields().Infinite().GAP()
    True
    sage: F.zero()        # workaround https://github.com/gap-system/gap/issues/517
    0
    sage: TestSuite(F).run(skip=skip)

    sage: F = mygap.SymmetricGroup(3); F
    Sym( [ 1 .. 3 ] )
    sage: F.category()
    Category of finite g a p groups
    sage: TestSuite(F).run(skip=skip)

    sage: F = mygap.FiniteField(3); F
    GF(3)
    sage: F in Fields().Finite().Enumerated().GAP()
    True
    sage: TestSuite(F).run(skip=skip) # not tested

Exploring functionalities from the Semigroups package::

    sage: H.is_r_trivial()                   # optional - semigroups
    True
    sage: H.is_l_trivial()                   # todo: not implemented in Semigroups; see https://bitbucket.org/james-d-mitchell/semigroups/issues/146/
    True

    sage: classes = H.j_classes(); classes   # optional - semigroups
    [ <Green's D-class: m1*m2*m1>, <Green's D-class: m1*m2>,
      <Green's D-class: m1>, <Green's D-class: m2*m1>,
      <Green's D-class: m2>, <Green's D-class: <identity ...>> ]

That's nice::

    sage: classes.category()                 # optional - semigroups
    Category of facade finite enumerated g a p sets
    sage: c = classes[0]; c                  # optional - semigroups
    <Green's D-class: m1*m2*m1>
    sage: c.category()                       # optional - semigroups
    Category of facade finite g a p greens class

    sage: pi1, pi2 = H.monoid_generators()
    sage: pi1^2 == pi1
    True

Apparently not available for this kind of monoids::

    sage: H.structure_description_schutzenberger_groups() # todo: not implemented


TODO and design discussions
===========================

- Better support for GAP lists and collections
- Better syntax for naming types / codomains
- fill in gap_category_to_structure from the info provided by @semantic


Vocabulary
----------

- "semantic handle" versus "handle" versus ???

User interface and features
---------------------------

- Keep the handle and the semantic handle separate or together?
- For a Sage object, what should .gap() return: a plain handle or a semantic handle
- For a semantic handle, what should .gap() return? Itself? In which case, we
  would systematically use ._libgap_() to retrieve the underlying libgap handle?
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
- Issue: How to support lazy imports?
- Issue: at this stage, Sage will associate a category C to its GAP
  counterpart only if C has been imported, so that the associated
  semantic information is inserted in the database


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

- Merge libgap / mygap
- Merging the code into Sage
"""
import itertools
import textwrap

from recursive_monkey_patch import monkey_patch
from sage.misc.cachefunc import cached_method
from sage.misc.nested_class import nested_pickle
from sage.misc.misc import attrcall
from sage.categories.category import Category
from sage.categories.objects import Objects
from sage.categories.sets_cat import Sets
#from sage.categories.magmas import Magmas
#from sage.categories.additive_semigroups import AdditiveSemigroups
#from sage.categories.additive_groups import AdditiveGroups
#from sage.categories.enumerated_sets import EnumeratedSets
#from sage.categories.modules import Modules
from sage.categories.rings import Rings
from sage.structure.element import Element
from sage.structure.parent import Parent
from sage.libs.gap.libgap import libgap
from sage.libs.gap.element import GapElement
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.misc.constant_function import ConstantFunction

##############################################################################
# Initialization
##############################################################################

import categories
import sage.categories
import categories.objects
import sage.categories.objects
monkey_patch(categories.objects, sage.categories.objects)

# Workaround until #27911 is merged
# libgap does not know about several functions
# This is a temporary workaround to let some of the tests run
import sage.libs.gap.gap_functions
sage.libs.gap.gap_functions.common_gap_functions.union(
    (["FreeMonoid", "IsRTrivial", "GreensJClasses", "GreensRClasses", "GreensLClasses", "GreensDClasses",
       "IsField", "FiniteField","LieAlgebra", "FullMatrixAlgebra", "ZmodnZ", "ApplicableMethod",
      "GeneratorsOfMonoid", "GeneratorsOfSemigroup",
      "GeneratorsOfAlgebra", "AdditiveInverse",
      "IsomorphismTransformationMonoid", "LieCentralizer",
      "LieNormalizer", "IsLieNilpotent", "IsRestrictedLieAlgebra",
      r"\+", r"\-", r"\*", r"\/"
  ]))

##############################################################################
# Code
##############################################################################

def GAP(gap_handle):
    """
    EXAMPLES::

        sage: from mygap import GAP
        sage: it = GAP(libgap([1,3,2]).Iterator())
        sage: for x in it: print(x)
        1
        3
        2
    """
    structure = retrieve_structure_of_gap_handle(gap_handle)
    return structure.cls(gap_handle, structure.category)

class MyGap(object):

    class Function:
        def __init__(self, f):
            self._f = f

        def __call__(self, *args):
            return GAP(self._f(*args))

    def __getattr__(self, name):
        return self.Function(libgap.__getattr__(name))

    def __call__(self, *args):
        return GAP(libgap(*args))

    def eval(self, code):
        """
        Return a semantic handle on the result of evaluating ``code`` in GAP.

        EXAMPLES::

            sage: from mygap import mygap
            sage: C = mygap.eval("Cyclotomics"); C
            Cyclotomics
            sage: C.gap().IsField()
            true
            sage: C in Fields().Infinite().GAP()
            True
        """
        return GAP(libgap.eval(code))

mygap = MyGap()


##############################################################################
# Classes for semantic handles

class GAPObject(object):
    def __init__(self, gap_handle, category=None):
        """

        EXAMPLES::

            sage: from mygap import mygap, GAPObject

            sage: GAPObject(libgap.FreeGroup(3))
            <mygap.GAPObject object at ...>
            sage: GAPObject(0)
            Traceback (most recent call last):
            ...
            ValueError: Not a handle to a gap object: 0

            sage: G = mygap.FreeGroup(3)
            sage: G(0)
            Traceback (most recent call last):
            ...
            ValueError: Not a handle to a gap object: 0
        """
        if not isinstance(gap_handle, GapElement):
            raise ValueError("Not a handle to a gap object: %s"%gap_handle)
        self._gap = gap_handle

    def gap(self):
        """
        Return the underlying libgap object.

        EXAMPLES::

            sage: from mygap import mygap
            sage: t = mygap.Transformation([1,3,2])
            sage: t1 = t._libgap_(); t1
            Transformation( [ 1, 3, 2 ] )

            sage: type(t1)
            <type 'sage.libs.gap.element.GapElement'>

        This hook is used by the ``libgap`` constructor::

            sage: t2 = libgap(t); t2
            Transformation( [ 1, 3, 2 ] )
            sage: l = libgap([t, t, t]); l
            [ Transformation( [ 1, 3, 2 ] ), Transformation( [ 1, 3, 2 ] ), Transformation( [ 1, 3, 2 ] ) ]

        TESTS:

        Both ``t._libgap_()`` and ``libgap(t)``  return the underlying ``libgap`` object::

            sage: t1 is t2
            True

        Currently, ``libgap`` seems to make copies in the above list construction::

            sage: l[1] is t1
            False
            sage: l[1] == t1
            True
        """
        return self._gap
    _libgap_ = gap                 # TODO: do we want to use ._libgap_() instead of .gap() everywhere?

    def _repr_(self):
        return repr(self.gap())
    __repr__ = _repr_

    def _wrap(self, obj):
        return GAP(obj)

    @cached_method
    def __hash__(self):
        return hash(self._repr_())

    def __cmp__(self, other): # Would be nicer to provide id as sorting key ...
        a = id(self)
        b = id(other)
        return (a > b) - (a < b)

    def __eq__(self, other):
        """
        Return whether ``self`` and ``other`` are equal.

        EXAMPLES::

            sage: from mygap import mygap
            sage: M = mygap.FreeMonoid(2)
            sage: M.category()
            Category of infinite g a p monoids
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

@nested_pickle
class GAPParent(GAPObject, Parent):
    def __init__(self, gap_handle, category=Sets()):
        Parent.__init__(self, category=category.GAP())
        GAPObject.__init__(self, gap_handle)

    #def _element_constructor(self, gap_handle):
    #    assert isinstance(gap_handle, sage.interfaces.gap.GapElement)
    #    return self.element_class(self, gap_handle)

    def _refine_category_(self, category=None):
        if category is None:
            structure = retrieve_structure_of_gap_handle(self.gap())
            assert structure.cls is GAPParent
            category = structure.category
        super(GAPParent, self)._refine_category_(category)

    class Element(GAPObject, Element):
        def __init__(self, parent, gap_handle):
            """
            Initialize an element of ``parent``

            .. TODO:: make this more robust

            """
            #from sage.libs.gap.element import GapElement
            #if not isinstance(gap_handle, GapElement):
            #    raise ValueError("Input not a GAP handle")
            Element.__init__(self, parent)
            GAPObject.__init__(self, gap_handle)

        def forget_parent(self):
            return GAP(self.gap())

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

class GAPIterator(GAPObject):

    def __iter__(self):
        """
        Return self, as per the iterator protocol.

        TESTS::

            sage: from mygap import GAPIterator
            sage: l = libgap([1,3,2])
            sage: it = GAPIterator(l.Iterator())
            sage: it.__iter__() is it
            True
        """
        return self


    def __next__(self):
        """
        Return the next object of this iterator or raise StopIteration, as
        per the iterator protocol.

        TESTS::

            sage: from mygap import GAPIterator
            sage: l = libgap([1,3,2])
            sage: it = GAPIterator(l.Iterator())
            sage: it.__next__()
            1
            sage: it.__next__()
            3
            sage: it.__next__()
            2
            sage: it.__next__()
            Traceback (most recent call last):
            ...
            StopIteration

            sage: for x in GAPIterator(l.Iterator()): print(x)
            1
            3
            2
        """
        if self.gap().IsDoneIterator():
            raise StopIteration
        return self.gap().NextIterator()

##############################################################################
# Retrieving the structure (class + category) to use for a semantic
# GAP handle from the properties of the underlying GAP object

class Structure:
    """
    A pair class + caegory
    """
    def __init__(self, cls, category):
        self.cls = cls
        self.category = category

    def __repr__(self):
        return repr((self.category, self.cls))

    def add_category(self, category):
        """
        Add a category

        EXAMPLES::

            sage: from mygap import Structure, GAPObject
            sage: s = Structure(GAPObject, Objects())
            sage: s.add_category(Magmas)
            sage: s.category
            Category of magmas
            sage: s.cls
            <class 'mygap.GAPParent'>
        """
        assert category is None or issubclass(category, Category)
        if not isinstance(category, Category):
            category = category.an_instance()
        if self.cls is GAPObject and category.is_subcategory(Sets()):
            self.cls = GAPParent
        self.category &= category

    def add_class(self, cls):
        """

        EXAMPLES::

            sage: from mygap import Structure, GAPObject, GAPMorphism
            sage: s = Structure(GAPObject, Objects())
            sage: s.add_class(GAPMorphism)
            sage: s.category
            Category of objects
            sage: s.cls
            <class 'mygap.GAPMorphism'>
        """
        assert issubclass(cls, self.cls)
        self.cls = cls

gap_category_to_structure = {
    "IsIterator":       attrcall("add_class", GAPIterator),
    # Cheating a bit: this should be IsMapping, which further requires IsTotal and IsSingleValued
    "IsGeneralMapping": attrcall("add_class", GAPMorphism),
}

true_properties_to_structure = {
    #"IsGroupAsSemigroup": add_axiom("Inverse"), # Useful?
}

false_properties_to_structure = {
}

def fill_allignment_database(cls):
    """
    Fill the database mapping gap categories / properties to their
    corresponding (super) Sage categories from the semantic
    information stored in the category class
    """
    assert issubclass(cls, Category)

    gap = cls._semantic.get("gap")
    gap_sub = cls._semantic.get("gap_sub", gap)
    gap_negation = cls._semantic.get("gap_negation")
    if gap_sub is not None:
        gap_category_to_structure[gap_sub] = attrcall("add_category", cls)
    if gap_negation is not None:
        false_properties_to_structure[gap_negation] = attrcall("add_category", cls)

def retrieve_structure_of_gap_handle(self):
    """
    Return the category corresponding to the properties and categories
    of the handled gap object.

    EXAMPLES::

        sage: import mygap
        sage: F = libgap.FreeGroup(3)
        sage: mygap.retrieve_structure_of_gap_handle(F)
        (Category of groups, <class 'mygap.GAPParent'>)

        sage: mygap.retrieve_structure_of_gap_handle(F.Iterator())
        (Category of objects, <class 'mygap.GAPIterator'>)

        sage: from mygap import mygap
        sage: mygap.FiniteField(3) in Fields().Finite().Enumerated().GAP()
        True

        sage: mygap.eval("Integers") in Rings().Commutative().GAP().Infinite()
        True
        sage: mygap.eval("Integers").category()
        Join of Category of commutative rings and Category of g a p monoids and Category of commutative g a p magmas and Category of finite dimensional g a p modules with basis over rings and Category of infinite g a p sets

        sage: mygap.eval("PositiveIntegers").category()
        Category of infinite commutative associative unital additive commutative additive associative distributive g a p magmas and additive magmas
        sage: mygap.eval("Cyclotomics") in Fields().Infinite().GAP()
        True
    """
    structure = Structure(GAPObject, Objects())
    gap_categories = [str(cat) for cat in self.CategoriesOfObject()]
    for cat in gap_categories:
        if cat in gap_category_to_structure:
            gap_category_to_structure[cat](structure)
    properties = set(str(prop) for prop in self.KnownPropertiesOfObject())
    true_properties = set(str(prop) for prop in self.KnownTruePropertiesOfObject())
    for prop in properties:
        if prop in true_properties:
            if prop in gap_category_to_structure:
                gap_category_to_structure[prop](structure)
        else:
            if prop in false_properties_to_structure:
                false_properties_to_structure[prop](structure)

    # Special cases that can't yet be handled by the infrastructure
    # - We don't have the LDistributive and RDistributive
    #   axioms, and the current infrastructure does not allow to make a
    #   "and" on two axioms "IsLDistributive": "Distributive"
    if "IsLDistributive" in true_properties and "IsRDistributive" in true_properties:
        # Work around: C._with_axiom("Distributive") does not work
        structure.category = structure.category.Distributive()
    if "IsMagmaWithInversesIfNonzero" in gap_categories and structure.category.is_subcategory(Rings()):
        structure.category = structure.category.Division()
    return structure

##############################################################################
# `typing` extensions to cast from a GAP handle

from sage_annotations.misc import sage_typing as typing

def Any_from_handle(self, handle):
    import mygap
    return mygap.GAP(handle)
typing.Any.__class__.from_handle = Any_from_handle
def GenericAlias_from_handle(self, handle):
    """
        sage: import typing, mygap
        sage: t = typing.List[int]
        sage: t.from_handle((1,2,3))
        [1, 2, 3]
    """
    container_type = self.__origin__
    if self.__args__ is None:
        return container_type(handle)
    if hasattr(container_type, "from_handle"):
        return container_type.from_handle(self, handle)
    value_type = from_handle(self.__args__[0])
    return container_type(value_type(x) for x in handle)
typing._GenericAlias.from_handle = GenericAlias_from_handle

def Facade_from_handle(self, handle):
    value_type = self.__args__[0]
    import mygap
    result = mygap.GAP(handle)
    result._refine_category_(result.category().Facade())
    result.facade_for = ConstantFunction(value_type)
    return result
typing.Facade.from_handle = Facade_from_handle

def Iterator_from_handle(self, handle):
    value_type = from_handle(self.__args__[0])
    import mygap
    return map(value_type, mygap.GAPIterator(handle))
typing.Iterator.from_handle = Iterator_from_handle

def from_handle(type):
    if hasattr(type, "from_handle"):
        return type.from_handle
    else:
        return type

##############################################################################
def gap_handle(x):
    """
    Return a low-level libgap handle to the corresponding GAP object.

    EXAMPLES::

        sage: from mygap import mygap, gap_handle
        sage: h = libgap.GF(3)
        sage: F = mygap(h)
        sage: gap_handle(F) is h
        True
        sage: l = gap_handle([1,2,F])
        sage: l
        [ 1, 2, GF(3) ]
        sage: l[0] == 1
        True
        sage: l[2] == h
        True

    .. TODO::

        Maybe we just want, for x a glorified hand, libgap(x) to
        return the corresponding low level handle
    """
    from mygap import GAPObject
    if isinstance(x, (list, tuple)):
        return libgap([gap_handle(y) for y in x])
    elif isinstance(x, GAPObject):
        return x.gap()
    else:
        return libgap(x)

##############################################################################

nested_classes_of_categories = [
    "ParentMethods",
    "ElementMethods",
    "MorphismMethods",
    "SubcategoryMethods",
]

def mmt_lookup_signature(*args):
    raise NotImplementedError

def generate_code(name, semantic):
    codomain = semantic.get("codomain")
    arity = semantic.get("arity")
    gap_name = semantic.get("gap")
    mmt_name = semantic.get("mmt")
    mmt_theory = semantic.get("mmt_theory")
    if gap_name is None: # codomain is None
        signature = None
        if mmt_name is not None:
            signature = mmt_lookup_signature(mmt_theory, mmt_name)
        if signature is not None:
            domains, codomain = signature
            if arity is None:
                arity = len(domains)
            else:
                arity == len(domains)
            # TODO: cleanup this logic
            if all(domain == codomain for domain in domains):
                codomain = typing.ParentOfSelf
                #assert self.codomain is None or codomain == self.codomain
    assert arity is not None
    assert gap_name is not None
    if codomain is None:
        codomain = typing.Any
    #assert isinstance(codomain, DependentType)
    def wrapper_method(self, *args):
        return from_handle(typing.specialize(codomain, self))(getattr(libgap, gap_name)(*gap_handle((self,)+args)))
    wrapper_method.__name__ = name
    wrapper_method.__doc__ = textwrap.dedent("""
    Wrapper around GAP's method {}

    arity: {}
    codomain: {}
    """).format(gap_name, arity, codomain)
    return wrapper_method

# Generate the GAP class
def generate_GAP_subcategory_class(cls):
    if not hasattr(cls, "_semantic"):
        return
    try:
        # Can't use cls.GAP because of the binding behavior
        GAP_cls = cls.__dict__['GAP']
    except KeyError:
        GAP_cls = type(cls.__name__+".GAP", (CategoryWithAxiom,), {})
        GAP_cls.__module__ = cls.__module__
        setattr(cls, 'GAP', GAP_cls)

    # Recurse in nested classes
    for name in nested_classes_of_categories:
        try:
            source = getattr(cls, name)
            semantic = getattr(source, "_semantic")
        except AttributeError:
            continue

        # Fetch the corresponding class in cls.GAP, creating it if needed
        try:
            target = getattr(GAP_cls, name)
        except AttributeError:
            target = type(name, (), {})
            setattr(GAP_cls, name, target)

        for (key, semantic) in semantic.items():
            setattr(target, key, generate_code(key, semantic))

# TODO: add a hook so that categories annotated later on get aligned
for cls in typing.annotated_categories:
    fill_allignment_database(cls)
    generate_GAP_subcategory_class(cls)
