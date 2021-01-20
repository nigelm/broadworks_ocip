# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Unreleased Changes
------------------

<!-- insertion marker -->
[1.4.0] - 2021-01-20
--------------------
- Updated Credits
- Fixed an error decoding an array of complex types, added test case
- Added little bit of documentation on return values.
- Added version number to README and top of documentation tree

[1.3.0] - 2021-01-18
--------------------
- Fixed problems with boolean response value decode (added tests)

[1.2.1] - 2020-12-01
--------------------
- Corrected the install information for the project

[1.2.0] - 2020-11-30
--------------------
- Add tests to show issues with ServiceProviderGetListResponse
- Fix echo="" attribute on responses command element
- Fix parsing of embedded subtypes due to incorrect method rename earlier
- Build XML generator for table elements

[1.1.1] - 2020-11-17
--------------------
- Moved the following classes into the module top level declarations:-
    - `ElementInfo`
    - `ErrorResponse`
    - `OCICommand`
    - `OCIRequest`
    - `OCIResponse`
    - `OCIType`
    - `SuccessResponse`
- Fixed some Makefile issues
- Internal documentation improvements
- Fixed the Changelog auto update

[1.0.1] - 2020-10-15
--------------------
- Reworked ElementInfo into attrs based class
- Various improvements to schema parsing into classes
- Session Id is no longer hidden on command classes
- Additional how/why documentation
- Converted to use poetry for development management

[0.5.3] - 2020-10-07
--------------------
- Occaisionally you can get an exception thrown on socket close as the
  api object is deleted.  Added try/except around this to catch.
- More log modifications - less opinionated
- Split traffic logging to a VERBOSE_DEBUG setting - log level 9

[0.5.2] - 2020-10-07
--------------------
- Logging was on at debug level by default - switched to WARNING level.

[0.5.1] - 2020-10-06
--------------------
- Removed a development debug print which had managed to stay hidden...

[0.5.0] - 2020-10-06
--------------------
- Reversed the stupid mistake of trying to special case complex types
  such as ``UnboundedPositiveInt`` - these now need to be treated as
  the complex types they are.

[0.4.0] - 2020-10-06
--------------------
- Split out handling in API of Types and Commands.
- This changes ``get_command_class()`` to ``get_type_class()`` and adds
  ``get_type_object()``

[0.3.1] - 2020-10-05
--------------------
- Fixed error where exception thrown as tests cleaned up.

[0.3.0] - 2020-10-01
--------------------
- Support for lists in XML generation
- Support for XSD choice elements - handled by making them optional
- Handling of embedded types in XML generation
- Start of special casing some base types - ie UnboundedPositiveInt

[0.2.0] - 2020-09-30
--------------------
- Support for list returns - eg ``ServiceProviderServicePackGetListResponse``

[0.1.0] - 2020-09-30
--------------------
- First release but not on PyPI.
- Patch releases on Pypi after automation sorted.
