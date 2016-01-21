from sage.categories.category_with_axiom import CategoryWithAxiom, all_axioms
from sage.misc.cachefunc import cached_method

class Magmas:
    class GAP(CategoryWithAxiom):

        class ElementMethods:

            def _mul_(self, other):
                r"""
                Return the product of self by other

                EXAMPLES::

                    sage: sys.path.insert(0, "./")
                    sage: from gap_sage import mygap
                    sage: G = mygap.FreeSemigroup(3)
                    sage: s1, s2, s3 = G.semigroup_generators()
                    sage: s1 * s3 * s2
                    s1*s3*s2
                """
                return self.parent(self.gap() * other.gap()) # TODO; call directly the gap operation

    class Unital:
        # TODO: this belongs to the main Sage categories
        class ElementMethods:
            def __div__(left, right):
                """
                Return the difference between ``left`` and ``right``, if it exists.

                This top-level implementation delegates the work to
                the ``_sub_`` method or to coercion. See the extensive
                documentation at the top of :ref:`sage.structure.element`.

                EXAMPLES::

                    sage: G = FreeGroup(2)
                    sage: x0, x1 = G.group_generators()
                    sage: c1 = cartesian_product([x0,x1])
                    sage: c2 = cartesian_product([x1,x0])
                    sage: c1.__div__(c2)
                    (x0*x1^-1, x1*x0^-1)
                    sage: c1 / c2
                    (x0*x1^-1, x1*x0^-1)

                Testing that division supports coercion::

                    sage: C = cartesian_product([G,G])
                    sage: H = Hom(G, C)
                    sage: phi = H(lambda g: cartesian_product([g, g]))
                    sage: phi.register_as_coercion()
                    sage: x1 / c1
                    (x1*x0^-1, 1)
                    sage: c1 / x1
                    (x0*x1^-1, 1)

                TESTS::

                    sage: c1.__div__.__module__
                    'categories.magmas'
                """
                from sage.structure.element import have_same_parent
                if have_same_parent(left, right):
                    return left._div_(right)
                from sage.structure.element import get_coercion_model
                import operator
                return get_coercion_model().bin_op(left, right, operator.div)

            def _div_(left, right):
                r"""
                Default implementation of division.

                EXAMPLES::

                    sage: G = FreeGroup(2)
                    sage: x0, x1 = G.group_generators()
                    sage: c1 = cartesian_product([x0,x1])
                    sage: c2 = cartesian_product([x1,x0])
                    sage: c1._div_(c2)
                    (x0*x1^-1, x1*x0^-1)

                TESTS::

                    sage: c1._div_.__module__
                    'categories.magmas'
                """
                return left._mul_(~right)


        class GAP(CategoryWithAxiom):
            class ParentMethods:
                def one(self):
                    return self(self.gap().One())

            class ElementMethods:
                def __invert__(self):
                    r"""
                    Return the inverse of this element.

                    EXAMPLES::

                        sage: sys.path.insert(0, "./")
                        sage: from gap_sage import mygap
                        sage: G = mygap.FreeGroup("a")
                        sage: a, = G.group_generators()
                        sage: a.__invert__()
                        a^-1
                        sage: a^-1
                        a^-1
                        sage: ~a
                        a^-1
                        sage: ~a * a
                        <identity ...>

                    This also works when inverses are defined everywhere but for zero::

                        sage: F = mygap.FiniteField(3)
                        sage: a = F.one(); a
                        Z(3)^0
                        sage: ~a
                        Z(3)^0
                        sage: ~(a+a)
                        Z(3)
                        sage: a = F.zero()
                        sage: ~a
                        Traceback (most recent call last):
                        ...
                        ValueError: 0*Z(3) is not invertible

                    .. WARN::

                        In other cases, GAP may return the inverse in
                        a larger domain without this being noticed by
                        Sage at this point::

                            sage: N = mygap.eval("Integers")
                            sage: x = N.one()

                        Probably acceptable::

                            sage: y = ~(x + x); y
                            1/2

                        Not acceptable::

                            sage: y.parent()
                            Integers

                    Should we have a category for the analogue of
                    MagmasWithInverseIfNonZero, and move this method
                    there?
                    """
                    from sage.libs.gap.libgap import libgap
                    fail = libgap.eval("fail")
                    inverse = self.gap().Inverse()
                    if inverse == fail:
                        raise ValueError("%s is not invertible"%self)
                    return self.parent()(inverse)
