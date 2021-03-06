# Internal Design

The intention was always to have a python class per OCICommand element from
the Broadworks AS schema.

To make this easier the `process_schema.py` program was produced to break
down the Broadworks schema into its component parts, which are represented as
python classes.

The classes are broken down into `types`, `requests` (commands that are
sent to the Broadworks system), and `responses` (the replies back from the
Broadworks system).

The classes themselves are described by a tuple of `ElementInfo` instances -
one per property in the schema class, and a class property for each schema
property.  Naming of these is in the more pythonic snake case rather than the
Java-esque CamelCase.

The ElementInfo class is used mainly to guide the XML serialisation and
deserialisation of each object.  They contain the python and XML names of each
property and some flags about the propery - for example is this a required
element `is_required`, an array like element `is_array`, a tabular set of
data `is_table` or a complex element (ie containing sub-elements)
`is_complex`.

All of the component classes of the system are intended to be immutable.
There are currently no helpers to aid creating a modified instance from an
existing instance because these operations do not appear to be part of a
normal Broadworks workflow.


## Implementation

The `ElementInfo` class was originally a named tuple, but this was changed
later to an [`attrs`](https://www.attrs.org/) based class for speed and to
give some type checking.

The generated classes are all based on Michael DeHaan's
[`ClassForge`](https://classforge.io/) object system. Although it  appears
that `attrs` can provide all the functionality these objects need, it became
apparent in testing that using `attrs` based classes added a substantial
startup cost to the library, which `ClassForge` does not.

Due to the huge number of component classes, and that they need to have the
session id associated with them on creation (since the objects themselves are
immutable), the `BroadworksAPI` class has a set of helper methods to create and
send the serialised commands to the server and then return the results.

In practice a user only interacts with the `BroadworksAPI` methods.


## Problems

There is no easy way that I can find - especially when autogenerated - to
replicate the XML schema `choice` elements - effectively a union between
different possibilities.  As such any element within a `choice` element has
been expressed as a non-required element, and it is up to the library user to
apply appropriate values to make the generated XML work.

As an example of this, look at the `UnboundedPositiveInt` elements within
the usage example, which may have either a positive numeric `quantity` value
or have `unlimited` set true.

Additionally in the example the surrounding `ServicePackAuthorization`
element may have either `unauthorized=True` or `authorized_quantity` set
to a `UnboundedPositiveInt`.

The tables returned in many command responses have no type information in the
schema as to how to treat them - the column information is also passed within
the response itself.  This means that often there are boolean or numeric
values that are represented as strings.  In particular the booleans will have
textual values of either `true` or `false` - all in lower case.
