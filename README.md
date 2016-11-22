# Experimenting with semantic handle interfaces between Sage and GAP

This module, built on top of libgap, enriches handles to GAP objects
by retrieving their mathematical properties from GAP, and exposing
them to Sage, to make them behave as native Sage objects.

## Usage examples

See the documentation at the top of the [mygap](mygap.py) module.

## Installation

Clone the repository, and run::

    sage -pip install .

If you plan to do development on this project, do instead:

    sage -pip install -e .

## Context and motivations

### The handle paradigm in system interfaces

The "handle" paradigm has become a classic when interfacing two
systems. Many of the SageMath interfaces, including the GAP, Singular,
or Pari interfaces use this paradigm to delegate calculations to those
systems.

In this paradigm, when a system `A` delegates a calculation to a
system `B`, the result `r` of the calculation is not converted to a
native `A` object; instead `B` just returns a handle (or reference) to
the object `r`. Later `A` can run further calculations with `r` by
passing it as argument to `B` functions or methods. Advantages of this
approach include:

- Avoiding the overhead of back and forth conversions between `A` and `B`.

- Manipulating objects of `B` from `A` even if they have no native
  representation in `A`.

### Semantic handle interfaces

Whenever `A` and `B` share some common semantic (for example the
concept of group), it's desirable that handles behave as native `A`
objects. For example, if a group `G` is constructed in `B`, one wants
to manipulate handles to `G` or its elements as if they were native
`A` groups or group elements, even if `G` is not natively implemented
in `A`. This is the usual *adapter* design pattern. The bulk of the
work is the implementation of adapter methods so that, for example,
calling the method `Gh.cardinality()` on a Sage handle `Gh` to a GAP
object `G`, triggers in GAP a call to `Size(G)`.

In Sage, this has been implemented in a couple special cases. For
examples, Sage permutation groups or matrix groups are built on top of
handles to GAP objects.

### Generic/hierarchical semantic handle interfaces

The above implementation is monolithic and does not scale. For
example, if `h` is a handle to a set `S`, Sage only knows that
`h.cardinality()` can be computed by `Size(S)` in GAP if `S` is a
group; in fact if `h` has been constructed through the
`PermutationGroup` or `MatrixGroup` constructors. Whereas we would
want this method to be available as soon as `S` is a set.


During the [first joint GAP-SageMath
days](http://gapdays.de/gap-sage-days2016/), Nicolas worked on a
prototype of generic semantic handle Sage-GAP interface. The idea is
twofold:

1.  Every Sage category (e.g. the category of sets, of groups) can
    provide a collection of adapter methods that are valid for every
    handle to a GAP object in the corresponding mathematical category.

2.  When a handle `h` to a GAP object `S` is created, the properties
    of `S` (it's GAP categories and properties) are explored, and the
    handle `h` is then put in the matching (or closest matching) Sage
    category.

At the current stage, and with the above, a handle to a GAP field
behaves essentially like a native Sage field (still experimental
though, and not foolproof). And this applies immediately to all
subcategories as well, from magmas to rings.

The infrastructure is relatively lightweight, and can be extended by
developers and users as the need for more adapter methods arises.

### Scaling to multisystem interfaces?

A second stage was initiated during the
[Knowledge representation in mathematical software and databases
workshop](http://opendreamkit.org/2015/12/08/WP6StAndrewsMeeting/)
organized at the University of St Andrews, St Andrews, 25th-27th January, 2016.

The approach described earlier works well for implementing an
interface between two systems. However it does not scale for
interfacing `n` systems, as this requires the implementation of
`n(n-1)` independent adapter interfaces.

The key point here is that implementing an adapter method or function
typically requires only some simple abstract information:

- the signature
- the name of the methods in both systems

In particular, the only thing that changes between an A-B adapter
method and the equivalent C-D adapter method is the names of the
methods.

The second stage of this project is therefore to explore whether the
interfaces could be automatically generated from a consistent
formalizations of the systems. Ideally, the mathematical structure and
operations would be described once, e.g. in the MMT language (the blue
blob in Michael's talk) and then each system would be formalized by
specifying how the operations are implemented (the purple blobs).

For example, one would specify in MMT that a magma is a set with a
binary operation denoted by default `o`. The relevant category in Sage
is `Magmas()`, and the binary operation is implemented by the method
`_mul_`.

Here we experiment with doing this formalization using lightweight
annotations in the Sage source code such as:

    @semantic(mmt="magmas")
    class Magmas(...):

        class ElementMethods:

             @semantic(mmt="o", gap="Product")
             @abstractmethod
             def _mul_(self, other):
                 r"""
                 Return the product of ``self`` by ``other``.

                 ...
                 """

Several variants of the annotations exist to allow for adding
annotations on existing categories without touching their file, and
also for specifying directly the corresponding method names in other
systems when this has not yet been formalized elsewhere. Similarly,
one could provide directly the signature information in case that is
not yet modelled in MMT.

### Difficulties

In Sage and GAP (and most other systems with some category mechanism)
we distinguish additive magma and multiplicative magma, duplicating
all the information, code, etc. In MMT however, thanks to morphisms
which allow to rename operations transparently, there is no such
distinction: there are just Magmas.

Hence, to actually map additive magmas in Sage to additive magmas in
GAP (and map the corresponding methods), one need in the intermediate
MMT step to keep an extra bit of information, namely whether the
monoid is additive or multiplicative (or something else; think of the
bracket operation of Lie algebras).


## Dependencies

The following are required by the automatically generated interface
using MMT.

    sudo apt-get install libxml2-dev libxslt1-dev
    sage -pip install lxml
    sage -python setup.py install

# Download all the MMT stuff (optional)

    mkdir MMT
    cd MMT
    wget https://github.com/KWARC/MMT/raw/gh-pages/deploy/mmt.jar
    git clone git@gl.mathhub.info:MMT/LATIN.git
    git clone git@gl.mathhub.info:MMT/urtheories.git
    git clone git@gl.mathhub.info:MMT/examples.git
    git clone git@gl.mathhub.info:ODK/MMTPy
