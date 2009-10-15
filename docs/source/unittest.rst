Unit Tests
==========

Pyogp unit testing ~ pyogp.lib.base contains internal tests that validate consistency of the library implementation. Using unittest and doctest, along with wsgi and mock objects, these tests simulate interaction with a grid where needed, or use predefined data where possible, to validate methods and such. 

Coverage is unfortunately sparse currently, though, enough examples exist and the api is generally stable enough that tests can reliably be created now.

Installing Nose
----------------

use Nose! http://somethingaboutorange.com/mrl/projects/nose/0.11.1/

Install Steps:

1. easy_install nose

- or -

1. http://somethingaboutorange.com/mrl/projects/nose/nose-0.11.1.tar.gz
2. gzip -dc nose-0.11.1.tar.gz | tar xf -
3. cd nose-0.11.1
4. python setup.py install 

Running Unit Tests
------------------

Against a checkout of a package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. nosetests --where={path to src/pyogp.lib.base}

2. see nosetests --help for more info 

3. disable library logging via setting Settings.ENABLE_LOGGING_IN_TESTS to False

When part of buildout
^^^^^^^^^^^^^^^^^^^^^

See `<http://wiki.secondlife.com/wiki/PyOGP_Package_Unittests>`_ for guidance on running tests when operating in pyogp's buildout.

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
