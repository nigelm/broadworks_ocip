=======
History
=======

0.1.0 (2020-09-30)
------------------

* First release but not on PyPI.
* Patch releases on Pypi after automation sorted.


0.2.0 (2020-09-30)
------------------

* Support for list returns - eg ``ServiceProviderServicePackGetListResponse``

0.3.0 (2020-10-01)
------------------

* Support for lists in XML generation
* Support for XSD choice elements - handled by making them optional
* Handling of embedded types in XML generation
* Start of special casing some base types - ie UnboundedPositiveInt

0.3.1 (2020-10-05)
------------------

* Fixed error where exception thrown as tests cleaned up.

0.4.0 (2020-10-06)
------------------

* Split out handling in API of Types and Commands.
* This changes ``get_command_class()`` to ``get_type_class()`` and adds
  ``get_type_object()``
