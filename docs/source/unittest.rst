Unit Tests
==========

Pyogp unit testing ~ pyogp.lib.base contains internal tests that validate consistency of the library implementation. Using unittest and doctest, along with wsgi and mock objects, these tests simulate interaction with a grid where needed, or use predefined data where possible, to validate methods and such. 

Coverage is unfortunately sparse currently, though, enough examples exist and the api is generally stable enough that tests can reliably be created now.

Running Unit Tests
------------------

To run unit tests:

1. navigate to a buildout checkout's root folder

2. run bin/client_unittest

    a. useful parameters:
    
        i. vv: enables printing of test names
        ii. (module name): run tests contained in a specific file
        iii. test-file-pattern=TEST_FILE_PATTERN: run modules where filename matches pattern
        iv. list: list all known tests

3. disable logging via setting ENABLE_LOGGING_IN_TESTS to False

Adding Tests
------------

doctest: add a {class}.txt file to pyogp.lib.base.tests.
unittest: add a test_{class}.py file to pyogp.lib.base.tests.

base.py ~ contains the wsgi handlers for certain mock objects (like MockXMLRPC, etc)

Current Tests
-------------

.. toctree::
  :glob: 

  unittest/*