"""
"Semantic aware" Sage interface to GAP

This module, built on top of libgap, enriches the handles to GAP
objects by retrieving their mathematical properties from GAP, and
exposing them to Sage, to make them behave as native Sage objects.

EXAMPLES:

Some initialization::

    sage: libgap.LoadPackage("semigroups")    # optional - semigroups Needed for some examples below
    true

    sage: from mygap import mygap

Let's construct a handle to a GAP permutation group::

    sage: G = mygap.Group(libgap.eval("[(1,2)(3,4), (5,6)]"))

This "semantic" handle is automatically recognized as a Sage group::

    sage: G in Groups()
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
    Category of finite gap groups

This category, together with its super categories of "GAP monoids",
"GAP magmas", etc, provide wrapper methods that translate the Sage
method calls to the corresponding GAP function calls.

Doing this using a hierarchy of categories allow to implement, for
example, once for all the wrapper method for multiplication (_mul_ ->
Prod) for all multiplicative structures in Sage.

Let's now consider a monoid::

    sage: M = mygap.FreeMonoid(2)
    sage: M.category()
    Category of infinite gap monoids

    sage: m1, m2 = M.monoid_generators()
    sage: m1 * m2 * m1 * m2
    (m1*m2)^2

We can now mix and match Sage and GAP elements::

    sage: C = cartesian_product([M, ZZ])
    sage: C.category()
    Category of Cartesian products of monoids
    sage: C.an_element()
    (m1, 1)

    sage: x = cartesian_product([m1,3])
    sage: y = cartesian_product([m2,5])
    sage: x*y
    (m1*m2, 15)

Here is a quotient monoid::

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
    <transformation monoid on 6 pts with 2 generators>

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


Let's construct a variety of GAP parents to check that they pass all
the generic tests; this means that they have a chance to behave
reasonably as native Sage parents::

    sage: skip = ["_test_pickling", "_test_elements"] # Pickling fails for now

    sage: F = mygap.eval("Cyclotomics"); F
    Cyclotomics
    sage: F.category()
    Category of infinite gap fields
    sage: F.zero()        # workaround https://github.com/gap-system/gap/issues/517
    0
    sage: TestSuite(F).run(skip=skip)

    sage: F = mygap.SymmetricGroup(3); F
    Sym( [ 1 .. 3 ] )
    sage: F.category()
    Category of finite gap groups
    sage: TestSuite(F).run(skip=skip)

    sage: F = mygap.FiniteField(3); F
    GF(3)
    sage: F.category()
    Category of finite gap fields
    sage: TestSuite(F).run(skip=skip)

Exploring functionalities from the Semigroups package::

    sage: H.is_r_trivial()                   # optional - semigroups
    True
    sage: H.is_l_trivial()                   # todo: not implemented in Semigroups; see https://bitbucket.org/james-d-mitchell/semigroups/issues/146/
    True

    sage: classes = H.j_classes(); classes   # optional - semigroups
    [ {m1*m2*m1}, {m2*m1}, {m1}, {m1*m2}, {m2}, {<identity ...>} ]

That's nice::

    sage: classes.category()                 # optional - semigroups
    Category of finite gap sets
    sage: c = classes[0]; c                  # optional - semigroups
    {m1*m2*m1}

That's not; we would want this to be a collection::

    sage: c.category()                       # optional - semigroups
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

- Merge libgap / mygap
- Merging the code into Sage
- Support for iterators
"""

import sys
sys.path.insert(0, "./")          # TODO

from misc.monkey_patch import monkey_patch
from sage.misc.cachefunc import cached_method
from sage.misc.nested_class import nested_pickle
from categories.lie_algebras import LieAlgebras
from sage.categories.objects import Objects
from sage.categories.sets_cat import Sets
from sage.categories.magmas import Magmas
from sage.categories.additive_semigroups import AdditiveSemigroups
from sage.categories.additive_groups import AdditiveGroups
from sage.categories.rings import Rings
from sage.structure.element import Element
from sage.structure.parent import Parent
from sage.libs.gap.libgap import libgap
from sage.libs.gap.element import GapElement

import categories
import sage.categories
import categories.objects
import sage.categories.objects
monkey_patch(categories.objects, sage.categories.objects)

if False: # Whether to use the explicit GAP categories (in categories/*), or anotations (in mmt.py)
    monkey_patch(categories, sage.categories)
else:
    import mmt

# libgap does not know about several functions
# This is a temporary workaround to let some of the tests run
import sage.libs.gap.gap_functions
sage.libs.gap.gap_functions.common_gap_functions.extend(
    (["FreeMonoid", "IsRTrivial", "JClasses", "IsField", "FiniteField",
      "LieAlgebra", "FullMatrixAlgebra", "ZmodnZ", "ApplicableMethod",
      "GeneratorsOfMonoid",
      r"\+", r"\-", r"\*", r"\/"
  ]))


def GAP(gap_handle):
    """
    EXAMPLES::

        sage: it = GAP(libgap([1,3,2]).Iterator())
        sage: for x in it: print x
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

            sage: C = mygap.eval("Cyclotomics"); C
            Cyclotomics
            sage: C.gap().IsField()
            true
            sage: C.category()
            Category of infinite gap fields
        """
        return GAP(libgap.eval(code))

mygap = MyGap()

class GAPObject(object):
    def __init__(self, gap_handle, category=None):
        """

        EXAMPLES::

            sage: from mygap import GAPObject
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
        super(GAPParent, self)._refine_category_(structure.category)

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

            sage: l = libgap([1,3,2])
            sage: it = GAPIterator(l.Iterator())
            sage: it.__iter__() is it
            True
        """
        return self


    def next(self):
        """
        Return the next object of this iterator or raise StopIteration, as
        per the iterator protocol.

        TESTS::

            sage: l = libgap([1,3,2])
            sage: it = GAPIterator(l.Iterator())
            sage: it.next()
            1
            sage: it.next()
            3
            sage: it.next()
            2
            sage: it.next()
            Traceback (most recent call last):
            ...
            StopIteration

            sage: for x in GAPIterator(l.Iterator()): print x
            1
            3
            2
        """
        if self.gap().IsDoneIterator():
            raise StopIteration
        return self.gap().NextIterator()

def add(category=None, cls=object):
    """

    EXAMPLES::

        sage: from mygap import add, Structure
        sage: s = Structure(object, Objects())
        sage: add(Magmas())(s)
        sage: s.category
        Category of magmas
        sage: s.cls
        <class 'mygap.GAPParent'>
    """
    if cls is object and category is not None and category.is_subcategory(Sets()):
        cls = GAPParent
    def f(structure):
        if cls is not None:
            assert issubclass(cls, structure.cls)
            structure.cls = cls
        if category is not None:
            structure.category &= category
    return f

def add_axiom(axiom):
    """

    EXAMPLES::

        sage: from mygap import add_axiom, Structure
        sage: s = Structure(object, Magmas())
        sage: add_axiom("Commutative")(s)
        sage: s.category
        Category of commutative magmas
        sage: s.cls
        <type 'object'>
    """
    def f(structure):
        structure.category = structure.category._with_axiom(axiom)
    return f

class Structure:
    def __init__(self, cls, category):
        self.cls = cls
        self.category = category

    def __repr__(self):
        return repr((self.category, self.cls))

gap_category_to_structure = {
    "IsMagma": add(Magmas()),
    "IsMagmaWithOne": add(Magmas().Unital()),
    "IsMagmaWithInverses": add(Magmas().Unital().Inverse()),

    # Note: Additive Magmas are always assumed to be associative and commutative in GAP
    # Near Additive Magmas don't require commutativity
    # See http://www.gap-system.org/Manuals/doc/ref/chap55.html
    "IsNearAdditiveMagma": add(AdditiveSemigroups()),
    "IsAdditiveMagma": add(AdditiveSemigroups().AdditiveCommutative()),
    "IsNearAdditiveMagmaWithZero": add(AdditiveSemigroups().AdditiveUnital()),
    # "IsMagmaWithInversesIfNonzero": 

    # Why isn't this a property?
    "IsNearAdditiveGroup": add(AdditiveGroups()),
    "IsIterator": add(cls=GAPIterator),
    # Cheating a bit: this should be IsMapping, which further requires IsTotal and IsSingleValued
    "IsGeneralMapping": add(cls=GAPMorphism, category=Sets()),
}

true_properties_to_structure = {
    "IsFinite": add_axiom("Finite"),
    "IsAssociative": add_axiom("Associative"),
    "IsCommutative": add_axiom("Commutative"),
    "IsMonoidAsSemigroup": add_axiom("Unital"),
    "IsGroupAsSemigroup": add_axiom("Inverse"), # Useful?
    "IsAdditivelyCommutative": add_axiom("AdditiveCommutative"),

    # Cheating: we don't have the LDistributive and RDistributive
    # axioms, and the current infrastructure does not allow to make a
    # "and" on two axioms
    # "IsLDistributive": "Distributive"

    # GAP's IsLieAlgebra is a filter to several properties,
    # IsAlgebra, IsZeroSquareRing, and IsJacobianRing
    "IsJacobianRing": add(LieAlgebras(Rings()))
}

false_properties_to_structure = {
    "IsFinite": add_axiom("Infinite"),
}

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
        sage: mygap.FiniteField(3).category()
        Category of finite gap fields
        sage: mygap.eval("Integers").category()
        Category of infinite commutative gap rings
        sage: mygap.eval("PositiveIntegers").category()
        Category of infinite commutative associative unital additive commutative additive associative distributive gap magmas and additive magmas
        sage: mygap.eval("Cyclotomics").category()
        Category of infinite gap fields
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
            if prop in true_properties_to_structure:
                true_properties_to_structure[prop](structure)
        else:
            if prop in false_properties_to_structure:
                false_properties_to_structure[prop](structure)

    # Special cases that can't be handled by the infrastructure
    if "IsLDistributive" in true_properties and "IsRDistributive" in true_properties:
        # Work around: C._with_axiom("Distributive") does not work
        structure.category = structure.category.Distributive()
    if "IsMagmaWithInversesIfNonzero" in gap_categories and structure.category.is_subcategory(Rings()):
        structure.category = structure.category.Division()
    return structure
