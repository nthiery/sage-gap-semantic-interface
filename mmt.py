# -*- coding: utf-8 -*-

"""
EXAMPLES::

    sage: from mygap import mygap
    sage: mygap.SymmetricGroup(3).an_element()
    (1,2,3)

    sage: G = Sp(4,GF(3))
    sage: G.random_element()  # random
    [2 1 1 1]
    [1 0 2 1]
    [0 1 1 0]
    [1 0 0 1]
    sage: G.random_element() in G
    True

    sage: F = GF(5); MS = MatrixSpace(F,2,2)
    sage: gens = [MS([[1,2],[-1,1]]),MS([[1,1],[0,1]])]
    sage: G = MatrixGroup(gens)
    sage: G.random_element()  # random
    [1 3]
    [0 3]
    sage: G.random_element().parent() is G
    True


Missing features
================

We would want to use F.random_element from ``Sets.GAP``, not
:class:`ModulesWithBasis` or :class:`FiniteEnumeratedSets`::

    sage: F = mygap.FiniteField(3); F
    GF(3)
    sage: F.category()
    Category of finite enumerated g a p fields
    sage: F.random_element.__module__
    'sage.categories.modules_with_basis'

Other issue: in GAP, a ring is considered as a (free) module over
itself, and GAP fields are set according to be vector spaces with
basis; see Fields.GAP.extra_super_categories::

    sage: F in VectorSpaces(Fields()).WithBasis()
    True

This is unlike Sage's fields::

    sage: GF(3) in VectorSpaces(Fields()).WithBasis()
    False

And can cause problems::

    sage: F.random_element()

We need a way (input syntax and datastructure) to represent various
types for the codomain (either passed to @semantic or recovered from
mmt). Examples:

    codomain=bool
    codomain=sage  -> call .sage
    codomain=self
    codomain=parent
    codomain=tuple(self)
    codomain=list(self)



>> namespace = XXXXX("u'http://latin.omdoc.org/math")
>> M = namespace.get_theory("Monoid")
>> u = M["universe"]     # Return the type of the elements of monoids  (MonoidElement?)
>> u = M["objects"]      # Return the type of the monoids (Monoid)
>> u = M["morphism"]     # Return the type of the monoid morphisms (MonoidMorphism)
>> u = M["homsets"]      # Return the type of the monoid homsets (MonoidHomset)
>> e = M["e"]            # Return the identity constant (note that e is not defined in Monoid but in NeutralElementLeft/Right)

e.return_type()           # Returns the type of the codomain

>> e.return_type() == u
True

>> e.arity()             # (or a way to recover it)
2

# Assume f is a function of type X -> (Y -> Z), then

>> f.return_type()
Z
>> f.argument_types()
[X,Y]
"""
import inspect
import itertools
import textwrap
from sage.misc.misc import attrcall
from functools import partial
from recursive_monkey_patch import monkey_patch

from sage.misc.abstract_method import abstract_method, AbstractMethod
from sage.categories.category import Category
from sage.categories.category_types import Category_over_base_ring
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.sets.family import Family
from sage.libs.gap.libgap import libgap
import sage.categories

def mmt_lookup_signature(mmt_theory, mmt_name):
    """
    EXAMPLES::

        sage: from mmt import mmt_lookup_signature
        sage: mmt_lookup_signature("Magma", u"∘")            # not tested
        ([OMID[u'http://latin.omdoc.org/math?Universe?u'],
          OMID[u'http://latin.omdoc.org/math?Universe?u']],
          OMID[u'http://latin.omdoc.org/math?Universe?u'])
    """
    from MMTPy.objects import path
    from MMTPy.connection import qmtclient
    from MMTPy.library.lf import wrappers

    # Create a client to connect to MMT
    q = qmtclient.QMTClient("http://localhost:8080/")

    # This is the namespace of the LATIN Math library
    latin_math = path.Path.parse("http://latin.omdoc.org")/"math"

    # We will now retrieve the types of an operation within that archive
    try:
        # build the path to the constant, in this case "∘", and request its type via MMT
        op_tp = q.getType(getattr(latin_math, mmt_theory)[mmt_name])

        # next we can unpack this function type into a triple of
        #(Type Variables, argument types, return type)
        (op_bd, op_tps, op_rt) = wrappers.lf_unpack_function_types(op_tp)
        return op_tps, op_rt
    except StandardError:
        return None


class MMTWrap:
    def __init__(self,
                 mmt_name=None,
                 variant=None,
                 module=None):
        self.mmt_name = mmt_name
        self.variant = variant

class DependentType:
    name = "a Type"
    @abstract_method
    def __call__(self, value):
        """
        Return the type for this value
        """
    def __init__(self, name=None):
        if name is not None:
            self.name = name

    def __repr__(self):
        return self.name

class ConstantType(DependentType):
    def __init__(self, type, name=None):
        DependentType.__init__(self, name)
        self.type = type

    def __call__(self, value):
        return self.type

import mygap

Any  = ConstantType(mygap.GAP, name="Any")
Sage = ConstantType(attrcall("sage"), name="Sage")
def GAPFacade(handle):
    result = GAP(handle)
    result._refine_category_(result.category().Facade())
    return result
Facade = ConstantType(GAPFacade, name="Facade")

class SelfClass(DependentType): # Singleton
    name = "Self"
    def __call__(self, value):
        return value
Self = SelfClass()

class ParentOfSelfClass(DependentType): # Singleton
    name = "ParentOfSelf"
    def __call__(self, value):
        return value.parent()
ParentOfSelf = ParentOfSelfClass()

class Iterator(DependentType):
    name = "Iterator"
    def __init__(self, value_type=Any):
        self.value_type = value_type

    def __repr__(self):
        return "{}({})".format(self.name, self.value_type)

    @staticmethod
    def from_handle(value_type, handle):
        return itertools.imap(value_type, GAPIterator(handle))

    def __call__(self, value):
        return partial(self.from_handle, self.value_type(value))

class Collection(Iterator):  # cheating a bit ...
    def __init__(self, container_type, value_type=Any, name=None):
        DependentType.__init__(self, name=name)
        self.container_type = container_type
        self.value_type = value_type

    def from_handle(self, value_type, handle):
        return self.container_type(value_type(x) for x in handle)

List    = partial(Collection, list, name="List")
Set     = partial(Collection, set,  name="Set")
Family  = partial(Collection, sage.sets.family.Family, name="Family")

"""
    sage: Any
    Any
    sage: Self
    Self
    sage: ParentOfSelf
    ParentOfSelf
    sage: Family(Iterator(Set(List(Self))))
    Family(Iterator(Set(List(Self))))
"""

def gap_handle(x):
    """
    Return a low-level libgap handle to the corresponding GAP object.

    EXAMPLES::

        sage: from mygap import mygap
        sage: from mmt import gap_handle
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

class MMTWrapMethod(MMTWrap):
    """

    .. TODO:: add real tests

    EXAMPLES::

        sage: from mmt import MMTWrapMethod
        sage: def zero(self):
        ....:     pass
        sage: f = MMTWrapMethod(zero, "0", gap_name="Zero")
        sage: c = f.generate_code("NeutralElement")
        sage: c
        <function zero at ...>
    """
    def __init__(self, f, mmt_name=None, gap_name=None, codomain=None, **options):
        MMTWrap.__init__(self, mmt_name, **options)
        self.__imfunc__= f
        self.gap_name = gap_name
        if not isinstance(codomain, DependentType) and codomain is not None:
            assert isinstance(codomain, type)
            codomain = ConstantType(codomain)
        self.codomain = codomain
        if isinstance(f, AbstractMethod):
            f = f._f
        argspec = sage.misc.sageinspect.sage_getargspec(f)
        self.arity = len(argspec.args)

    def generate_code(self, mmt_theory):
        codomain = self.codomain
        arity = self.arity
        gap_name = self.gap_name
        if gap_name is None: # codomain is None
            signature = mmt_lookup_signature(mmt_theory, self.mmt_name)
            if signature is not None:
                domains, codomain = signature
                arity = len(domains)
                if self.arity is not None:
                    assert self.arity == arity
                # TODO: cleanup this logic
                if all(domain == codomain for domain in domains):
                    codomain = ParentOfSelf
                    assert self.codomain is None or codomain == self.codomain
        assert arity is not None
        assert gap_name is not None
        if codomain is None:
            codomain = Any
        assert isinstance(codomain, DependentType)
        def wrapper_method(self, *args):
            return codomain(self)(getattr(libgap, gap_name)(*gap_handle((self,)+args)))
        wrapper_method.__name__ = self.__imfunc__.__name__
        wrapper_method.__doc__ = textwrap.dedent("""
        Wrapper around GAP's method {}

        arity: {}
        codomain: {}
        """).format(gap_name, arity, codomain)
        return wrapper_method

nested_classes_of_categories = [
    "ParentMethods",
    "ElementMethods",
    "MorphismMethods",
    "SubcategoryMethods",
]

def generate_interface(cls, mmt=None, gap=None, gap_super=None, gap_sub=None, gap_negation=None):
    """
    INPUT:
    - ``cls`` -- the class of a category
    - ``mmt`` -- a string naming an mmt theory
    - ``gap`` -- a string naming a gap property/category
    """
    import mygap

    # Fetch cls.GAP, creating it if needed
    try:
        # Can't use cls.GAP because of the binding behavior
        GAP_cls = cls.__dict__['GAP']
    except KeyError:
        GAP_cls = type(cls.__name__+".GAP", (CategoryWithAxiom,), {})
        GAP_cls.__module__ = cls.__module__
        setattr(cls, 'GAP', GAP_cls)

    # Store the semantic information for later use
    cls._semantic={
        'gap': gap,
        'gap_sub': gap_sub,
        'gap_super': gap_super,
        'gap_negation': gap_negation,
        'mmt': mmt,
    }

    # Fill the database mapping gap categories / properties to their
    # corresponding (super) Sage categories
    if gap_sub is None:
        gap_sub = gap
    if gap_sub is not None or gap_negation is not None:
        def fill_allignment_database(cls, source=None):
            assert issubclass(cls, Category)
            import mygap
            if gap_sub is not None:
                mygap.gap_category_to_structure[gap_sub] = mygap.add(category=cls)
            if gap_negation is not None:
                mygap.false_properties_to_structure[gap_negation] = mygap.add(category=cls)
        if issubclass(cls, Category):
            fill_allignment_database(cls)
        else:
            # cls is a fake class whose content will be monkey patched to an actual category
            # Delay the database filling until the monkey patching, so
            # that will actually know the category class
            cls._monkey_patch_hook = classmethod(fill_allignment_database)

    # Recurse in nested classes
    for name in nested_classes_of_categories:
        try:
            source = getattr(cls, name)
        except AttributeError:
            continue
        # Fetch the corresponding class in cls.GAP, creating it if needed
        try:
            target = getattr(GAP_cls, name)
        except AttributeError:
            target = type(name, (), {})
            setattr(GAP_cls, name, target)
        nested_class_semantic = {}
        for (key, method) in source.__dict__.items():
            if key in {'__module__', '__doc__'}:
                continue
            assert isinstance(method, MMTWrapMethod)
            nested_class_semantic[key] = {
                "__imfunc__": method.__imfunc__,
                "codomain" : method.codomain,
                "gap_name" : method.gap_name,
                "mmt_name" : method.mmt_name
            }
            setattr(target, key, method.generate_code(mmt))
            setattr(source, key, method.__imfunc__)
        source._semantic = nested_class_semantic

def semantic(mmt=None, variant=None, codomain=None, gap=None, gap_negation=None, gap_sub=None, gap_super=None):
    def f(cls_or_function):
        if inspect.isclass(cls_or_function):
            cls = cls_or_function
            generate_interface(cls, mmt=mmt, gap=gap, gap_negation=gap_negation, gap_sub=gap_sub, gap_super=gap_super)
            return cls
        else:
            return MMTWrapMethod(cls_or_function,
                                 mmt_name=mmt,
                                 variant=variant,
                                 codomain=codomain,
                                 gap_name=gap)
    return f

@semantic(mmt="Set")
class Sets:
    class ParentMethods:
        @semantic(gap="IsFinite", codomain=Sage)
        @abstract_method
        def is_finite(self):
            pass

        @semantic(gap="Size", codomain=Sage)
        @abstract_method
        def cardinality(self):
            pass

        @semantic(gap="Representative", codomain=Self)
        @abstract_method
        def _an_element_(self):
            pass

        @semantic(gap="Random", codomain=Self)
        @abstract_method
        def random_element(self):
            pass

    @semantic(mmt="TODO", gap="IsFinite")
    class Finite:
        class ParentMethods:
            @semantic(gap="List", codomain=List(Self))
            @abstract_method
            def list(self):
                pass

    @semantic(gap_negation="IsFinite")
    class Infinite:
        pass
monkey_patch(Sets, sage.categories.sets_cat.Sets)

@semantic(mmt="TODO")
class EnumeratedSets:
    class ParentMethods:
        @semantic(gap="Iterator", codomain=Iterator(Self))
        @abstract_method
        def __iter__(self):
            pass
    @semantic(gap_sub="IsList")
    class Finite:
        pass

    @semantic()
    class Facade(CategoryWithAxiom):
        class ParentMethods:
            @semantic(gap="Iterator", codomain=Iterator(Any))
            @abstract_method
            def __iter__(self):
                pass
monkey_patch(EnumeratedSets, sage.categories.enumerated_sets.EnumeratedSets)

# class Lists:
#     def super_categories(self):
#         return EnumeratedSets().Finite()
#     class ParentMethods:
#         @semantic(gap="")
#         @abstract_method
#         def __getitem__(self):
#             pass

@semantic(mmt="Magma", variant="additive")
class AdditiveMagmas:
    class ElementMethods:
        @semantic(mmt=u"∘", gap=r"\+", codomain=ParentOfSelf) #, operator="+")
        @abstract_method
        def _add_(self, other):
            pass

    @semantic(mmt="NeutralElement", variant="additive", gap="IsAdditiveMagmaWithZero")
    class AdditiveUnital:
        class ParentMethods:
            # Defined in NeutralElementLeft
            # - How to retrieve it?
            # - How to detect that this is a method into self?
            @semantic(mmt="neutral", gap="Zero", codomain=Self)
            @abstract_method
            def zero(self):
                # Generates automatically in the XXX.GAP category
                # def zero(self): return self(self.gap().Zero())
                pass

        class ElementMethods:
            @semantic(gap=r"\-", codomain=ParentOfSelf)
            @abstract_method
            def _sub_(self, other):
                # Generates automatically
                # def _sub_(self,other): return self(gap.Subtract(self.gap(), other.gap()))
                pass

            # TODO: Check Additive Inverse
            @semantic(gap="AdditiveInverse", codomain=ParentOfSelf)
            @abstract_method
            def __neg__(self):
                # Generates automatically
                # def _neg_(self): return self.parent()(self.gap().AdditiveInverse())
                pass

    @semantic(gap="IsAdditivelyCommutative")
    class AdditiveCommutative:
        pass
monkey_patch(AdditiveMagmas, sage.categories.additive_magmas.AdditiveMagmas)

@semantic(mmt="Magma", gap="IsMagma", variant="multiplicative")
class Magmas:
    class ElementMethods:
        @semantic(mmt="*", gap=r"\*", codomain=ParentOfSelf) #, operator="*"
        @abstract_method
        def _mul_(self, other):
            pass

    class ParentMethods:
        one = semantic(mmt="neutral", gap="One", codomain=Self)(sage.categories.magmas.Magmas.Unital.ParentMethods.__dict__['one'])

    @semantic(mmt="NeutralElement", gap="IsMagmaWithOne")
    class Unital:
        class ParentMethods:
            # Defined in NeutralElementLeft
            # - How to retrieve it?
            # - How to detect that this is a method into self?
            #one = semantic(mmt="neutral", gap="One", codomain=Self)(sage.categories.magmas.Magmas.Unital.ParentMethods.__dict__['one'])
            #@abstract_method
            #def one(self):
            #    # Generates automatically in the XXX.GAP category
            #    # def one(self): return self(self.gap().One())
            #    pass
            pass

        class ElementMethods:
            @semantic(mmt="inverse", gap="Inverse", codomain=ParentOfSelf)
            @abstract_method
            def __invert__(self): # TODO: deal with "fail"
                pass

        @semantic(gap="IsMagmaWithInverses")
        class Inverse:
            pass

    @semantic(gap="IsCommutative")
    class Commutative:
        pass

monkey_patch(Magmas, sage.categories.magmas.Magmas)

# In GAP, NearAdditiveMagma assumes associative and AdditiveMagma
# further assumes commutative.

@semantic(mmt="Semigroup", variant="additive", gap="IsNearAdditiveMagma")
class AdditiveSemigroups:
    # Additive Magmas are always assumed to be associative and commutative in GAP
    # Near Additive Magmas don't require commutativity
    # See http://www.gap-system.org/Manuals/doc/ref/chap55.html

    @semantic(gap="IsAdditiveMagma")
    class AdditiveCommutative:
        pass

    # In principle this is redundant with isAdditiveMagmaWithZero
    # specified above; however IsAdditiveMagmaWithZero does not
    # necessarily appear in the categories of an additive gap monoid
    @semantic(gap="IsNearAdditiveMagmaWithZero")
    class AdditiveUnital:
        @semantic(gap="IsNearAdditiveGroup")
        class AdditiveInverse:
            pass
monkey_patch(AdditiveSemigroups, sage.categories.additive_semigroups.AdditiveSemigroups)

@semantic(mmt="Semigroup", variant="multiplicative", gap="IsAssociative")
class Semigroups:
    class ParentMethods:
        @semantic(gap="GeneratorsOfSemigroup", codomain=Family(Self))
        @abstract_method
        def semigroup_generators(self):
            pass

        @semantic(gap="\/")
        @abstract_method
        def __truediv__(self, relations):
            pass

        @semantic(gap="IsLTrivial", codomain=bool)
        @abstract_method
        def is_l_trivial(self):
            pass

        @semantic(gap="IsRTrivial", codomain=bool)
        @abstract_method
        def is_r_trivial(self):
            pass

        @semantic(gap="IsDTrivial", codomain=bool)
        @abstract_method
        def is_d_trivial(self):
            pass

    @semantic()
    class Finite:
        class ParentMethods:
            @semantic(gap="GreensJClasses", codomain=Facade)
            @abstract_method
            def j_classes(self):
                pass

            @semantic(gap="GreensLClasses", codomain=Facade)
            @abstract_method
            def l_classes(self):
                pass

            @semantic(gap="GreensRClasses", codomain=Facade)
            @abstract_method
            def r_classes(self):
                pass

            @semantic(gap="GreensDClasses", codomain=Facade)
            @abstract_method
            def d_classes(self):
                pass

            @semantic(gap="StructureDescriptionMaximalSubgroups")
            @abstract_method
            def structure_description_maximal_subgroups(self):
                pass

            @semantic(gap="StructureDescriptionSchutzenbergerGroups")
            @abstract_method
            def structure_description_schutzenberger_groups(self):
                pass

            @semantic(gap="IsomorphismTransformationSemigroup")
            @abstract_method
            def isomorphism_transformation_semigroup(self):
                pass

    @semantic(gap="IsMonoidAsSemigroup")
    class Unital:
        class ParentMethods:
            @semantic(gap="GeneratorsOfMonoid", codomain=Family(Self))
            @abstract_method
            def monoid_generators(self):
                pass

        @semantic()
        class Finite:
            class ParentMethods:
                @semantic(gap="IsomorphismTransformationMonoid")
                @abstract_method
                def isomorphism_transformation_monoid(self):
                    pass

monkey_patch(Semigroups, sage.categories.semigroups.Semigroups)

@semantic(gap="IsGreensClass")
class GreensClass(Category):
    def super_categories(self):
        return [sage.categories.sets_cat.Sets()]

    class ParentMethods:
        @semantic(gap="SchutzenbergerGroup")
        def schutzenberger_group(self):
            pass

@semantic(mmt="Group", variant="multiplicative")
class Groups:

    class ParentMethods:

        @semantic(gap="IsAbelian", codomain=Sage)
        @abstract_method
        def is_abelian(self):
            pass

        @semantic(gap="GeneratorsOfGroup", codomain=Family(Self))
        @abstract_method
        def group_generators(self):
            pass

        @semantic(gap="\/")
        @abstract_method
        def __truediv__(self, relators):
            pass
monkey_patch(Groups, sage.categories.groups.Groups)


sage.categories.modules.Modules.WithBasis.FiniteDimensional # workaround: triggers the lazy import
@semantic(mmt="Modules")
class Modules:
    @semantic(gap="IsFreeLeftModule") # TODO: check that this is exactly equivalent
    class WithBasis:
        @semantic(gap="IsFiniteDimensional")
        class FiniteDimensional:
            class ParentMethods:
                @semantic(gap="Dimension", codomain=Sage)
                @abstract_method # FIXME: this overrides ModulesWithBasis.ParentMethods.dimension
                def dimension(self):
                    pass

                # TODO: find an idiom when you want to specify the semantic of
                # a method in a subcategory of where it's defined, and don't
                # want to override the original
                @semantic(gap="Basis", codomain=Family(Self))
                @abstract_method
                def basis_disabled(self):
                    pass
monkey_patch(Modules, sage.categories.modules.Modules)

from sage.categories.magmatic_algebras import MagmaticAlgebras
# This should be gap_super="IsJacobianRing", and we would need to
# recover the other filters "IsLieAlegbra" is composed of.  This will
# do for now
@semantic(mmt="LieAlgebra", gap="IsJacobianRing")
class LieAlgebras(Category_over_base_ring):

    r"""
    A class for Lie algebras.

    The implementation is as handles to GAP objects.

    EXAMPLE::

        sage: from mmt import LieAlgebras
        sage: L = LieAlgebras(Rings()).GAP().example()
        sage: L
        <Lie algebra over Rationals, with 2 generators>
        sage: L.category()
        Category of finite dimensional g a p lie algebras with basis over rings
        sage: Z = L.lie_center()
        sage: Z
        <Lie algebra of dimension 0 over Rationals>
        sage: Z.category()
        Category of finite finite dimensional commutative associative g a p lie algebras with basis over rings
        sage: L     # we know more after computing the center!
        <Lie algebra of dimension 3 over Rationals>
        sage: CZ = L.lie_centralizer(Z)
        sage: CZ
        <Lie algebra of dimension 3 over Rationals>
        sage: CZ.category()
        Category of finite dimensional g a p lie algebras with basis over rings
        sage: CL = L.lie_centralizer(L)
        sage: CL
        <Lie algebra of dimension 0 over Rationals>
        sage: NL = L.lie_normalizer(L)
        sage: NL
        <Lie algebra of dimension 3 over Rationals>
        sage: NZ = L.lie_normalizer(Z)
        sage: NZ
        <Lie algebra of dimension 3 over Rationals>
        sage: L.lie_derived_subalgebra()
        <Lie algebra of dimension 3 over Rationals>
        sage: L.lie_nilradical()
        <Lie algebra of dimension 0 over Rationals>
        sage: L.lie_solvable_radical()
        <Lie algebra of dimension 0 over Rationals>
        sage: L.cartan_subalgebra()
        <Lie algebra of dimension 1 over Rationals>
        sage: L.lie_derived_series()
        [<Lie algebra of dimension 3 over Rationals>]
        sage: L.lie_derived_series()[0]
        <Lie algebra of dimension 3 over Rationals>
        sage: L.lie_lower_central_series()
        [<Lie algebra of dimension 3 over Rationals>]
        sage: L.lie_upper_central_series()
        [<Lie algebra over Rationals, with 0 generators>]
        sage: L.is_lie_abelian()
        False
        sage: Z.is_lie_abelian()
        True
        sage: L.is_lie_nilpotent()
        False
        sage: L.is_lie_solvable()
        False
        sage: L.semi_simple_type()
        'A1'
        sage: L.chevalley_basis()
        [ [ LieObject( [ [ 0, 1 ], [ 0, 0 ] ] ) ],
          [ LieObject( [ [ 0, 0 ], [ 1, 0 ] ] ) ],
          [ LieObject( [ [ 1, 0 ], [ 0, -1 ] ] ) ] ]
        sage: L.root_system()
        <mygap.GAPObject object at 0x...>
        sage: L.root_system().gap()
        <root system of rank 1>
        sage: L.is_restricted_lie_algebra()
        False
    """
    def super_categories(self):
        """
        EXAMPLES::

            sage: from mmt import LieAlgebras
            sage: LieAlgebras(Rings()).super_categories()
            [Category of magmatic algebras over rings]
        """
        return [MagmaticAlgebras(self.base_ring())]

    class ParentMethods:

        @semantic(mmt="TODO", gap="GeneratorsOfAlgebra", codomain=List(Self)) # TODO: tuple_of_self
        @abstract_method
        def lie_algebra_generators(self):
            r"""
            Return generators for this Lie algebra.

            OUTPUT:

                A tuple of elements of ``self``

            EXAMPLES::

                sage: from mmt import LieAlgebras
                sage: L = LieAlgebras(Rings()).GAP().example()
                sage: a, b = L.lie_algebra_generators()
                sage: a, b
                (LieObject( [ [ 0, 1 ],
                              [ 0, 0 ] ] ),
                 LieObject( [ [ 0, 0 ],
                              [ 1, 0 ] ] ))
            """
            # return tuple(self(handle) for handle in self.gap().GeneratorsOfAlgebra())
            pass

        @semantic(mmt="TODO", gap="LieCentre") # TODO: codomain
        def lie_center(self):
            pass

        @semantic(mmt="TODO", gap="LieCentralizer") # TODO: codomain
        def lie_centralizer(self, S):
            pass

        @semantic(mmt="TODO", gap="LieNormalizer") # TODO: codomain
        def lie_normalizer(self, U):
            pass

        @semantic(mmt="TODO", gap="LieDerivedSubalgebra") # TODO: codomain
        def lie_derived_subalgebra():
            pass

        @semantic(mmt="TODO", gap="LieNilRadical") # TODO: codomain
        def lie_nilradical():
            pass

        @semantic(mmt="TODO", gap="LieSolvableRadical") # TODO: codomain
        def lie_solvable_radical():
            pass

        @semantic(mmt="TODO", gap="CartanSubalgebra") # TODO: codomain
        def cartan_subalgebra():
            pass

        @semantic(mmt="TODO", gap="LieDerivedSeries", codomain=List())
        def lie_derived_series():
            pass

        @semantic(mmt="TODO", gap="LieLowerCentralSeries", codomain=List())
        def lie_lower_central_series():
            pass

        @semantic(mmt="TODO", gap="LieUpperCentralSeries", codomain=List())
        def lie_upper_central_series():
            pass

        @semantic(mmt="TODO", gap="IsLieAbelian", codomain=bool)
        def is_lie_abelian():
            pass

        @semantic(mmt="TODO", gap="IsLieNilpotent", codomain=bool)
        def is_lie_nilpotent():
            pass

        @semantic(mmt="TODO", gap="IsLieSolvable", codomain=bool)
        def is_lie_solvable():
            pass

        @semantic(mmt="TODO", gap="SemiSimpleType", codomain=Sage)
        def semi_simple_type():
            pass

        # TODO: so far the 2 following methods return GAP objects

        @semantic(mmt="TODO", gap="ChevalleyBasis") # TODO: codomain
        def chevalley_basis():
            pass

        @semantic(mmt="TODO", gap="RootSystem") # TODO: codomain
        def root_system():
            pass

        @semantic(mmt="TODO", gap="IsRestrictedLieAlgebra", codomain=bool)
        def is_restricted_lie_algebra():
            pass

    class ElementMethods:
        pass

    class GAP(CategoryWithAxiom):
        def example(self):
            r"""
            Return an example of Lie algebra.

            EXAMPLE::

                sage: from mmt import LieAlgebras
                sage: LieAlgebras(Rings()).GAP().example()
                <Lie algebra over Rationals, with 2 generators>
            """
            from mygap import mygap
            from sage.matrix.constructor import matrix
            from sage.rings.rational_field import QQ
            a = matrix([[0, 1],
                        [0, 0]])
            b = matrix([[0, 0],
                        [1, 0]])
            return mygap.LieAlgebra( QQ, [a, b] )

class Category_over_base_ring:
    @classmethod
    def an_instance(cls):
        return cls(sage.categories.rings.Rings())
monkey_patch(Category_over_base_ring, sage.categories.category_types.Category_over_base_ring)

class Fields:
    class GAP(CategoryWithAxiom):
        def extra_super_categories(self):
            return [sage.categories.modules.Modules(sage.categories.rings.Rings()).FiniteDimensional()]

    class Finite:
        class GAP(CategoryWithAxiom):
            def extra_super_categories(self):
                return [sage.categories.enumerated_sets.EnumeratedSets()]

monkey_patch(Fields, sage.categories.fields.Fields)
