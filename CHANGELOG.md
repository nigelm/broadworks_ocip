# Changelog
All notable changes to this project will be documented in this file.
This is now automatically updated by `python-semantic-release`.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!--next-version-placeholder-->

## v2.0.1 (2022-03-12)
### Fix
* Handle schema sequences within choices ([`16c2e75`](https://github.com/nigelm/broadworks_ocip/commit/16c2e7509336f59f6af13710ecff6edaa08aa897))

### Documentation
* Add note about command construction and checking ([`56cb717`](https://github.com/nigelm/broadworks_ocip/commit/56cb717cdcc0abc4bc626918985d7d92acf44782))

## v2.0.0 (2022-03-05)
### Feature
* Broadworks R24 schemas and derived files ([`c0c71c3`](https://github.com/nigelm/broadworks_ocip/commit/c0c71c33234806329c48651272cb128b96fd3b27))
* Change base classes to be a custom object ([`6d89b0d`](https://github.com/nigelm/broadworks_ocip/commit/6d89b0dc392cfdb52974641fce2c560d99ae2011))
* Convert all base classes from classforge to attrs ([`0132a21`](https://github.com/nigelm/broadworks_ocip/commit/0132a211337f905918641c9fda548edc396f6e08))

### Fix
* Work round issues in Broadworks R24 schemas ([`85c1902`](https://github.com/nigelm/broadworks_ocip/commit/85c19023eb021edc40086d3dda6079e5586ae7db))
* Tweaks to the trivial live test program ([`45c37c8`](https://github.com/nigelm/broadworks_ocip/commit/45c37c86cd6492a536f36075fb508ba74d31de3f))
* Ensure session_id is put into received objects ([`b594669`](https://github.com/nigelm/broadworks_ocip/commit/b5946695e98ccaf7cc0ec7396c7b0482d09bf07b))
* Add __str__ and __repr__ methods ([`6797801`](https://github.com/nigelm/broadworks_ocip/commit/6797801fcea1743c6307341c34c8c4e111796dfc))
* Tweaked command to_dict() to put session first ([`4024d50`](https://github.com/nigelm/broadworks_ocip/commit/4024d509da3abe90a88233bcb881e87a79a58c01))
* Tweaked tests to avoid spurious mypy error ([`81ae17e`](https://github.com/nigelm/broadworks_ocip/commit/81ae17ebdf3a7d96a232afe01db4d2fe78d76462))
* Regenerate all the derived files ([`4b76a8b`](https://github.com/nigelm/broadworks_ocip/commit/4b76a8b30a84c75019cfeba585dc877b85deba33))
* Make black reformatting of generated files selectable ([`2b17390`](https://github.com/nigelm/broadworks_ocip/commit/2b17390db7759781617b5e31f22c7d8658ba6eb9))
* Process_schema now produces markdown docs ([`a47fa13`](https://github.com/nigelm/broadworks_ocip/commit/a47fa1342b23830772f2b8eda7ee1beb5bcbdb7a))
* Doc and return type improvements ([`47dd765`](https://github.com/nigelm/broadworks_ocip/commit/47dd765ff71705cd30e9b7d0e55fe4b2a9af6807))
* Better type markup ([`89a9446`](https://github.com/nigelm/broadworks_ocip/commit/89a944668c7d7158333ce0953c5a1ffbca4ecf7f))
* Corrected type annotations ([`7fef38e`](https://github.com/nigelm/broadworks_ocip/commit/7fef38e2cdcd806a257d9e8f0132bc42fcf384d8))
* Class slots do not include attributes of super class ([`a6d4d11`](https://github.com/nigelm/broadworks_ocip/commit/a6d4d117f2920f2766b39fe0711a96952b681a6a))
* Regenerate the generated modules ([`9ab0066`](https://github.com/nigelm/broadworks_ocip/commit/9ab0066ec07b1395efc56453eacd72c753bc7001))
* Removed dead code ([`7360a7f`](https://github.com/nigelm/broadworks_ocip/commit/7360a7f397ea2c68977f2f14fba6d6b3135beabe))
* Schema processor now outputs attrs based classes ([`4e96e82`](https://github.com/nigelm/broadworks_ocip/commit/4e96e8200d0146c29f07955bd1797b2b8b931bfa))

### Breaking
* This release changes to a different underlying class system - which should not have any user visible issues other than there are now no longer the full set of basic methods on an object that the old ClassForge base gave.  Additionally the classes are generated from the Broadworks R24 schemas.  ([`61c292d`](https://github.com/nigelm/broadworks_ocip/commit/61c292dc01020d700653f4d30e5c65937a7ddddb))

### Documentation
* More README updates ([`61c292d`](https://github.com/nigelm/broadworks_ocip/commit/61c292dc01020d700653f4d30e5c65937a7ddddb))
* Update README info ([`30e4a29`](https://github.com/nigelm/broadworks_ocip/commit/30e4a29ed2b12024dc62bc0c2f12618409c30ed1))

[1.5.0] - 2022-01-13
--------------------
- Change schema processor to pick up many more places where array values are
  appropriate. This is going to break the API signature for a lot of
  functions - although not likely to be ones people were using considering
  this has been broken for a while.
- chore: update dependencies
- ci: update pre-commit rules
- test: added test for UserVoiceMessagingUserModifyVoiceManagementRequest
- Added two more example tests for complex commands
- Update dependancies include pre-commit
- Updated dependencies
- Added request/response/type docs to API docs
- Additional test/sample of complex command


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
