==========================
Broadworks OCI-P Interface
==========================


.. image:: https://img.shields.io/pypi/v/broadworks_ocip.svg
        :target: https://pypi.python.org/pypi/broadworks_ocip

.. image:: https://img.shields.io/travis/nigelm/broadworks_ocip.svg
        :target: https://travis-ci.com/nigelm/broadworks_ocip

.. image:: https://readthedocs.org/projects/broadworks-ocip/badge/?version=latest
        :target: https://broadworks-ocip.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Interfaces to the OCI-P provisioning interface of a Broadworks softswitch


* Free software: BSD license
* Documentation: https://broadworks-ocip.readthedocs.io.


Features
--------

* python objects to match all Broadworks schema objects
* API framework to talk to a Broadworks server
* additional magic to handle authentication and sessions
* Based on Broadworks schema R21


Usage
-----

More details is given within the usage section of the documentation, but the
minimal summary is::

    from broadworks_ocip import BroadworksAPI

    # configure the API, connect and authenticate to the server
    api = BroadworksAPI(
        host=args.host, port=args.port, username=args.username, password=args.password,
    )

    # get the platform software level
    response = api.command("SystemSoftwareVersionGetRequest")
    print(response.version)


Credits
-------

The class is built using Michael DeHaan's `ClassForge`_ object system.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _ClassForge: https://classforge.io/
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
