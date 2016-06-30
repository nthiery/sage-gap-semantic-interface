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

We would want to use F.random_element from ``Sets.GAP``, not :class:`FiniteEnumeratedSets`:

        sage: F = mygap.FiniteField(3); F
        GF(3)
        sage: F.category()
        Category of finite g a p fields
        sage: F.random_element.__module__
        'sage.categories.finite_enumerated_sets'

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
from recursive_monkey_patch import monkey_patch

from sage.misc.abstract_method import abstract_method, AbstractMethod
from sage.categories.category_types import Category_over_base_ring
from sage.categories.category_with_axiom import CategoryWithAxiom
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
        self.codomain = codomain
        if isinstance(f, AbstractMethod):
            f = f._f
        self.arity = f.__code__.co_argcount

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
                    codomain = "parent"
                    assert self.codomain is None or codomain == self.codomain
        assert arity is not None
        assert gap_name is not None
        if codomain == "parent":
            def wrapper_method(self, *args):
                return self.parent()(getattr(libgap, gap_name)(*gap_handle((self,)+args)))
        elif codomain == "self":
            def wrapper_method(self, *args):
                return self(getattr(libgap, gap_name)(*gap_handle((self,)+args)))
        elif codomain == "list_of_self":
            def wrapper_method(self, *args):
                return [self(x) for x in getattr(libgap, gap_name)(*gap_handle((self,)+args))]
        elif codomain == "iter_of_self":
            def wrapper_method(self, *args):
                from mygap import GAPIterator
                return itertools.imap(self, GAPIterator(getattr(libgap, gap_name)(*gap_handle((self,)+args))))
        elif codomain == "sage":
            def wrapper_method(self, *args):
                return getattr(libgap, gap_name)(*gap_handle((self,)+args)).sage()
        else:
            assert codomain is None
            def wrapper_method(self, *args):
                return self._wrap(getattr(libgap, gap_name)(*gap_handle((self,)+args)))
        wrapper_method.__name__ = self.__imfunc__.__name__
        return wrapper_method

nested_classes_of_categories = {
    "ParentMethods": "parent",
    "ElementMethods": "element",
    "MorphismMethods": "morphism",
    "SubcategoryMethods": "subcategory"
}

def generate_interface(cls, mmt_theory):
    """
    INPUT:
    - ``cls`` -- the class of a cls
    - ``mmt_theory`` -- an mmt theory
    """
    # Fetch cls.GAP, creating it if needed
    try:
        # Can't use cls.GAP because of the binding behavior
        GAP_cls = cls.__dict__['GAP']
    except KeyError:
        GAP_cls = type(cls.__name__+".GAP", (CategoryWithAxiom,), {})
        GAP_cls.__module__ = cls.__module__
        setattr(cls, 'GAP', GAP_cls)

    cls._semantic={
        'gap': gap,
        'mmt': mmt,
    }
    for name in nested_classes_of_categories.keys():
        nested_class_semantic = {}
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
            setattr(target, key, method.generate_code(mmt_theory))
            setattr(source, key, method.__imfunc__)
        cls._semantic[nested_classes_of_categories[name]] = nested_class_semantic


def semantic(mmt=None, variant=None, codomain=None, gap=None):
    def f(cls_or_function):
        if inspect.isclass(cls_or_function):
            cls = cls_or_function
            generate_interface(cls, mmt=mmt, gap=gap)
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
        @semantic(gap="IsFinite", codomain="sage")
        @abstract_method
        def is_finite(self):
            pass

        @semantic(gap="Size", codomain="sage")
        @abstract_method
        def cardinality(self):
            pass

        @semantic(gap="Representative", codomain="self")
        @abstract_method
        def _an_element_(self):
            pass

        @semantic(gap="Random", codomain="self")
        @abstract_method
        def random_element(self):
            pass

    @semantic(mmt="TODO")
    class Finite:
        class ParentMethods:
            @semantic(gap="List", codomain="list_of_self")
            @abstract_method
            def list(self):
                pass
monkey_patch(Sets, sage.categories.sets_cat.Sets)

@semantic(mmt="TODO")
class EnumeratedSets:
    class ParentMethods:
        @semantic(gap="Iterator", codomain="iter_of_self")
        @abstract_method
        def __iter__(self):
            pass
monkey_patch(EnumeratedSets, sage.categories.enumerated_sets.EnumeratedSets)

@semantic(mmt="Magma", variant="additive")
class AdditiveMagmas:
    class ElementMethods:
        @semantic(mmt=u"∘", gap=r"\+", codomain="parent") #, operator="+")
        @abstract_method
        def _add_(self, other):
            pass

    @semantic("NeutralElement")
    class AdditiveUnital:
        class ParentMethods:
            # Defined in NeutralElementLeft
            # - How to retrieve it?
            # - How to detect that this is a method into self?
            @semantic(mmt="neutral", gap="Zero", codomain="self")
            @abstract_method
            def zero(self):
                # Generates automatically in the XXX.GAP category
                # def zero(self): return self(self.gap().Zero())
                pass

        class ElementMethods:
            @semantic(gap=r"\-", codomain="parent")
            @abstract_method
            def _sub_(self, other):
                # Generates automatically
                # def _sub_(self,other): return self(gap.Subtract(self.gap(), other.gap()))
                pass

            @semantic(gap="AdditiveInverse", codomain="parent")
            @abstract_method
            def __neg__(self):
                # Generates automatically
                # def _neg_(self): return self.parent()(self.gap().AdditiveInverse())
                pass
monkey_patch(AdditiveMagmas, sage.categories.additive_magmas.AdditiveMagmas)

@semantic(mmt="Magma", variant="multiplicative")
class Magmas:
    class ElementMethods:
        @semantic(mmt="*", gap=r"\*", codomain="parent") #, operator="*"
        @abstract_method
        def _mul_(self, other):
            pass

    @semantic("NeutralElement")
    class Unital:
        class ParentMethods:
            # Defined in NeutralElementLeft
            # - How to retrieve it?
            # - How to detect that this is a method into self?
            @semantic(mmt="neutral", gap="One", codomain="self")
            @abstract_method
            def one(self):
                # Generates automatically in the XXX.GAP category
                # def zero(self): return self(self.gap().One())
                pass

        class ElementMethods:

            @semantic(mmt="inverse", gap="Inverse", codomain="parent")
            @abstract_method
            def __invert__(self): # TODO: deal with "fail"
                pass
monkey_patch(Magmas, sage.categories.magmas.Magmas)

@semantic(mmt="Semigroup", variant="additive")
class AdditiveSemigroups:
    pass
monkey_patch(AdditiveSemigroups, sage.categories.additive_semigroups.AdditiveSemigroups)

@semantic(mmt="Semigroup", variant="multiplicative")
class Semigroups:
    class ParentMethods:
        @semantic(gap="GeneratorsOfSemigroup", codomain="list_of_self") # TODO: tuple_of_self
        @abstract_method
        def semigroup_generators(self):
            pass

        @semantic(gap="\/")
        @abstract_method
        def __truediv__(self, relations):
            pass

        @semantic(gap="IsLTrivial")
        @abstract_method
        def is_l_trivial(self):
            pass

        @semantic(gap="IsRTrivial")
        @abstract_method
        def is_r_trivial(self):
            pass

        @semantic(gap="IsDTrivial")
        @abstract_method
        def is_d_trivial(self):
            pass

    @semantic()
    class Finite:
        class ParentMethods:
            @semantic(gap="JClasses")
            @abstract_method
            def j_classes(self):
                pass

            @semantic(gap="LClasses")
            @abstract_method
            def l_classes(self):
                pass

            @semantic(gap="RClasses")
            @abstract_method
            def r_classes(self):
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

    @semantic()
    class Unital:
        class ParentMethods:
            @semantic(gap="GeneratorsOfMonoid", codomain="list_of_self") # TODO: tuple_of_self
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

@semantic(mmt="Group", variant="multiplicative")
class Groups:

    class ParentMethods:

        @semantic(gap="IsAbelian", codomain="sage")
        @abstract_method
        def is_abelian(self):
            pass

        @semantic(gap="GeneratorsOfGroup", codomain="list_of_self") # TODO: tuple_of_self
        @abstract_method
        def group_generators(self):
            pass

        @semantic(gap="\/")
        @abstract_method
        def __truediv__(self, relators):
            pass
monkey_patch(Groups, sage.categories.groups.Groups)

from sage.categories.magmatic_algebras import MagmaticAlgebras
@semantic(mmt="LieAlgebra")
class LieAlgebras(Category_over_base_ring):

    r"""
    A class for Lie algebras.

    The implementation is as handles to GAP objects.
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

        @semantic(mmt="TODO", gap="GeneratorsOfAlgebra", codomain="list_of_self") # TODO: tuple_of_self
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

        @semantic(mmt="TODO", gap="LieDerivedSeries") # TODO: codomain
        def lie_derived_series():
            pass

        @semantic(mmt="TODO", gap="LieLowerCentralSeries") # TODO: codomain
        def lie_lower_central_series():
            pass

        @semantic(mmt="TODO", gap="LieUpperCentralSeries") # TODO: codomain
        def lie_upper_central_series():
            pass

        @semantic(mmt="TODO", gap="IsLieAbelian") # TODO: codomain
        def is_lie_abelian():
            pass

        @semantic(mmt="TODO", gap="IsLieNilpotent") # TODO: codomain
        def is_lie_nilpotent():
            pass

        @semantic(mmt="TODO", gap="IsLieSolvable") # TODO: codomain
        def is_lie_solvable():
            pass

        @semantic(mmt="TODO", gap="SemiSimpleType") # TODO: codomain
        def semi_simple_type():
            pass

        @semantic(mmt="TODO", gap="ChevalleyBasis") # TODO: codomain
        def chevalley_basis():
            pass

        @semantic(mmt="TODO", gap="RootSystem") # TODO: codomain
        def root_system():
            pass

        @semantic(mmt="TODO", gap="IsRestrictedLieAlgebra") # TODO: codomain
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
