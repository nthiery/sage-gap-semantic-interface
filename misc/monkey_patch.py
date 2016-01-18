import pkgutil
from types import ModuleType, ClassType
from sage.categories.category_singleton import Category_singleton

def monkey_patch(source, target, verbose=False):
    """
    EXAMPLES::

        sage: sys.path.insert(0, "/home/nthiery/Sage-Combinat/sage-semigroups/")

        sage: from sage_semigroups.misc.monkey_patch import monkey_patch

        sage: class A(object):
        ....:     def f(self):
        ....:         return "calling A.f"
        ....:     def g(self):
        ....:         return "calling A.g"
        ....:     class Nested:
        ....:         pass

        sage: a = A()
        sage: a.f()
        'calling A.f'
        sage: a.g()
        'calling A.g'

        sage: class AMonkeyPatch:
        ....:     def f(self):
        ....:         return "calling AMonkeyPatch.f"
        ....:     class Nested:
        ....:         def f(self):
        ....:             return "calling AMonkeyPatch.Nested.f"

        sage: monkey_patch(AMonkeyPatch, A)

        sage: a.f()
        'calling AMonkeyPatch.f'
        sage: a.g()
        'calling A.g'
        sage: a_nested = A.Nested()
        sage: a_nested.f()
        'calling AMonkeyPatch.Nested.f'

        sage: a = A()
        sage: a.f()
        'calling AMonkeyPatch.f'
        sage: a.g()
        'calling A.g'
        sage: a_nested = A.Nested()
        sage: a_nested.f()
        'calling AMonkeyPatch.Nested.f'
    """
    if verbose:
        print "Monkey patching %s into %s"%(source.__name__, target.__name__)
    if isinstance(source, ModuleType):
        assert isinstance(target, ModuleType)
        if hasattr(source, "__path__"):
            # Recurse into package
            for (module_loader, name, ispkg) in pkgutil.iter_modules(path=source.__path__, prefix=source.__name__+"."):
                subsource = module_loader.find_module(name).load_module(name)
                short_name = name.split('.')[-1]
                if short_name in target.__dict__:
                    subtarget = target.__dict__[short_name]
                    assert isinstance(subtarget, (type, ModuleType))
                    monkey_patch(subsource, subtarget, verbose=verbose)

    for (key, subsource) in source.__dict__.iteritems():
        if isinstance(source, ModuleType) and \
           not (hasattr(subsource, "__module__") and subsource.__module__ == source.__name__):
            continue
        if isinstance(subsource, (type, ClassType)) and key in target.__dict__:
            # Recurse into class
            subtarget = target.__dict__[key]
            assert isinstance(subtarget, (type, ClassType))
            monkey_patch(subsource, subtarget, verbose=verbose)
            continue
        if key == "__doc__" and subsource is None:
            continue
        setattr(target, key, subsource)

    if isinstance(target, type) and issubclass(target, Category_singleton):
        category = target.an_instance()
        for cls_key, category_key in (("ParentMethods", "parent_class"),
                                      ("ElementMethods", "element_class"),
                                      ("MorphismMethods", "morphism_class"),
                                      ("SubcategoryMethods", "subcategory_class")):
            if cls_key in source.__dict__:
                monkey_patch(source.__dict__[cls_key], getattr(category, category_key), verbose=verbose)

