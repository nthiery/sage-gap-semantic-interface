# -*- coding: utf-8 -*-

"""
EXAMPLES::

    sage: sys.path.insert(0, "./")
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
        Category of finite gap fields
        sage: F.random_element.__module__
        'sage.categories.finite_enumerated_sets'


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
import importlib

from sage.misc.abstract_method import abstract_method, AbstractMethod
from sage.categories.category import Category
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.libs.gap.libgap import libgap

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
        f = self.__imfunc__
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
                return self.parent()(getattr(libgap, gap_name)(*[arg.gap() for arg in (self,)+args]))
        elif codomain == "self":
            def wrapper_method(self, *args):
                return self(getattr(libgap, gap_name)(*[arg.gap() for arg in (self,)+args]))
        elif codomain == "list_of_self":
            def wrapper_method(self, *args):
                return [self(x) for x in getattr(libgap, gap_name)(*[arg.gap() for arg in (self,)+args])]
        else:
            assert codomain is None
            def wrapper_method(self, *args):
                return self._wrap(getattr(libgap, gap_name)(*[arg.gap() for arg in (self,)+args]))
        wrapper_method.__name__ = self.__imfunc__.__name__
        return wrapper_method

class MMTWrapClass(MMTWrap):
    def __init__(self, cls, mmt_name, **options):
        MMTWrap.__init__(self, mmt_name, **options)
        self.cls = cls

def generate_interface(source, target, mmt_theory):
    """ INPUT: two classes """
    if issubclass(target, Category):
        GAP_category = type(target.__name__+".GAP", (CategoryWithAxiom,), {})
        GAP_category.__module__ = target.__module__
        setattr(target, 'GAP', GAP_category)
        #assert isinstance(source, MMTWrapClass)
        for name, subsource in source.__dict__.items():
            # Handle special cases
            if name in ["ParentMethods", "ElementMethods", "MorphismMethods", "SubcategoryMethods"]:
                subtarget = type(name, (), {})
                setattr(GAP_category, name, subtarget)
                generate_interface(subsource, subtarget, mmt_theory)

            # Recurse into nested categories
            if isinstance(subsource, MMTWrap):
                assert isinstance(subsource, MMTWrapClass)
                assert name in target.__dict__
                subtarget = target.__dict__[name]
                assert issubclass(subtarget, CategoryWithAxiom)
                generate_interface(subsource.cls, subtarget, subsource.mmt_name)
    else:
        # source and target are plain bags of methods
        for (name, method) in source.__dict__.items():
            if name in {'__module__', '__doc__'}:
                continue
            assert isinstance(method, MMTWrapMethod)
            setattr(target, name, method.generate_code(mmt_theory))


def semantic(mmt=None, variant=None, module_name=None, codomain=None, gap=None):
    def f(cls_or_function):
        # Temporarily wrap the object for later reuse
        if inspect.isclass(cls_or_function):
            cls_or_function = MMTWrapClass(cls_or_function,
                                           mmt_name=mmt,
                                           variant=variant)
        else:
            cls_or_function = MMTWrapMethod(cls_or_function,
                                            mmt_name=mmt,
                                            variant=variant,
                                            codomain=codomain,
                                            gap_name=gap)

        if module_name is not None:
            # Retrieve the actual Sage category
            category_name = cls_or_function.cls.__name__
            module = importlib.import_module(module_name)
            category = getattr(module, category_name)

            # Generate the interface by walking recursively through the tree
            generate_interface(cls_or_function.cls, category, mmt)
        return cls_or_function
    return f

@semantic(mmt="Set", module_name="sage.categories.sets_cat")
class Sets:
    class ParentMethods:
        @semantic(gap="IsFinite")
        def is_finite(self):
            pass

        @semantic(gap="Size")
        def cardinality(self):
            pass

        @semantic(gap="Representative", codomain="self")
        def _an_element_(self):
            pass

        @semantic(gap="Random", codomain="self")
        def random_element(self):
            pass

    @semantic(mmt="TODO")
    class Finite:
        class ParentMethods:
            @semantic(gap="List", codomain="list_of_self")
            def list(self):
                pass

@semantic(mmt="TODO", module_name="sage.categories.enumerated_sets")
class EnumeratedSets:
    class GAP(CategoryWithAxiom):
        class ParentMethods:
            def __iter__(self):
                """
                EXAMPLES::

                    sage: sys.path.insert(0, "./")
                    sage: from mygap import mygap
                    sage: F = mygap.FiniteField(3)
                    sage: for x in F: # indirect doctest
                    ....:     print x
                    0*Z(3)
                    Z(3)^0
                    Z(3)

                    sage: for x in F: # indirect doctest
                    ....:     assert x.parent() is F
                """
                return itertools.imap(self, self._wrap(self.gap().Iterator()))

@semantic(mmt="Magma", variant="additive", module_name="sage.categories.additive_magmas")
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
                pass

            # Generates automatically in the XXX.GAP category
            # def zero(self): return self(self.gap().Zero())

        class ElementMethods:
            @semantic(gap=r"\-", codomain="parent")
            @abstract_method
            def _sub_(self, other):
                pass

            # Generates automatically
            # def _sub_(self,other): return self(gap.Subtract(self.gap(), other.gap()))


@semantic(mmt="Semigroup")
class AdditiveSemigroups:
    pass

@semantic(mmt="Ring")
class Rings:
    pass
