# -*- coding: utf-8 -*-

"""
namespace = XXXXX("u'http://latin.omdoc.org/math")

>>> M = namespace.get_theory("Monoid")
>>> u = M["universe"]     # Return the type of the elements of monoids  (MonoidElement?)
>>> u = M["objects"]      # Return the type of the monoids (Monoid)
>>> u = M["morphism"]     # Return the type of the monoid morphisms (MonoidMorphism)
>>> u = M["homsets"]      # Return the type of the monoid homsets (MonoidHomset)
>>> e = M["e"]            # Return the identity constant (note that e is not defined in Monoid but in NeutralElementLeft/Right)

e.return_type()           # Returns the type of the codomain

>>> e.return_type() == u
True

>>> e.arity()             # (or a way to recover it)
2

# Assume f is a function of type X -> (Y -> Z), then

>>> f.return_type()
Z
>>> f.argument_types()
[X,Y]
"""



import inspect
import importlib

from sage.misc.abstract_method import abstract_method
from sage.categories.category import Category
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.libs.gap.libgap import libgap

def mmt_lookup_signature(mmt_theory, mmt_name):
    """
    EXAMPLES::

        sage: from mmt import mmt_lookup_signature
        sage: mmt_lookup_signature("Magma", u"∘")
        ([OMID[u'http://latin.omdoc.org/math?Universe?u'],
          OMID[u'http://latin.omdoc.org/math?Universe?u']],
          OMID[u'http://latin.omdoc.org/math?Universe?u'])
    """
    from MMTPy.objects import path
    from MMTPy.connection import qmtclient
    from MMTPy.library.lf import wrappers
    from MMTPy.declarations import declaration

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
                 mmt_name,
                 variant=None,
                 module=None):
        self.mmt_name = mmt_name
        self.variant = variant

class MMTWrapMethod(MMTWrap):
    """

    EXAMPLES::

        sage: from mmt import MMTWrapMethod
        sage: def zero(self):
        ....      pass
        sage: f = MMTWrapMethod(zero, "0", gap="Zero")
        sage: c = f.generate_code()
        sage: c

    """
    def __init__(self, f, mmt_name, gap_name=None, inner=None, **options):
        MMTWrap.__init__(self, mmt_name, **options)
        self.__imfunc__= f
        self.gap_name = gap_name
        self.inner = inner
        # self.arity = self.__imfunc__.__code__.co_argcount
        # For an abstract method we need to fetch _f first
        self.arity = self.__imfunc__._f.__code__.co_argcount

    def generate_code(self, mmt_theory):
        if self.inner is None or self.gap_name is None:
            signature = mmt_lookup_signature(mmt_theory, self.mmt_name)
            if signature is not None:
                domains, codomain = signature
                arity = len(domains)
                if self.arity is not None:
                    assert self.arity == arity
                inner = all(domain == codomain for domain in domains)
                if self.inner is not None:
                    assert inner == self.inner
            else:
                inner = self.inner
                gap_name = self.gap_name
        assert self.inner is not None
        assert self.arity is not None
        if inner:
            def wrapper_method(self, *args):
                return self.parent()(getattr(libgap, gap_name)(*[arg.gap() for arg in (self,)+args]))
        else:
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


def mmt(mmt_name, variant=None, module_name=None, inner=None, gap_name=None):
    def f(cls_or_function):
        # Temporarily wrap the object for later reuse
        if inspect.isclass(cls_or_function):
            cls_or_function = MMTWrapClass(cls_or_function,
                                           mmt_name=mmt_name,
                                           variant=variant)
        else:
            cls_or_function = MMTWrapMethod(cls_or_function,
                                            mmt_name=mmt_name,
                                            variant=variant,
                                            inner=inner,
                                            gap_name=gap_name)

        if module_name is not None:
            # Retrieve the actual Sage category
            category_name = cls_or_function.cls.__name__
            module = importlib.import_module(module_name)
            category = getattr(module, category_name)

            # Generate the interface by walking recursively through the tree
            generate_interface(cls_or_function.cls, category, mmt_name)
        return cls_or_function
    return f


@mmt("Magma", "additive", module_name="sage.categories.additive_magmas")
class AdditiveMagmas:

    class ElementMethods:

        @mmt(u"∘", gap_name=r"\+") #, operator="+")
        @abstract_method
        def _add_(self, other):
            pass

    @mmt("NeutralElement")
    class AdditiveUnital:
        class ParentMethods:
            # Defined in NeutralElementLeft
            # - How to retrieve it?
            # - How to detect that this is an inner method?
            @mmt("neutral", gap_name="Zero", inner=True)
            @abstract_method
            def zero(self):
                pass

            # Generates automatically in the XXX.GAP category
            # def zero(self): return self(self.gap().Zero())

        class ElementMethods:
            @mmt("-", inner=True, gap_name=r"\-")
            @abstract_method
            def _sub_(self, other):
                pass

            # Generates automatically
            # def _sub_(self,other): return self(gap.Subtract(self.gap(), other.gap()))


@mmt("Semigroups")
class AdditiveSemigroups:
    pass

@mmt("Ring")
class Rings:
    pass
