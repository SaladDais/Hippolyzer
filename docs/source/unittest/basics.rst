basics
======


.. module:: pyogp.lib.base.network.tests.basics

This is a doctest, the content here is verbatim from the source file at pyogp.lib.base.network.tests.basics.txt.


Networking Basics
~~~~~~~~~~~~~~~~~

The networking layer is basically a replaceable REST client. It is defined as a utility
providing methods such as GET, POST etc.

Let's retrieve the standard utility (this is overridden here in this test to use a mockup network library):

>>> from pyogp.lib.base.exc import HTTPError
>>> from pyogp.lib.base.tests.mockup_client import MockupClient
>>> from pyogp.lib.base.tests.base import StdLibClient
>>> client = MockupClient(StdLibClient())

Now we can use it. Let's post something to our test server:

>>> response = client.GET('http://localhost:12345/network/get')
>>> response.body
'Hello, World'

Let's try a 404:

>>> client.GET('http://localhost:12345/foobar')
Traceback (most recent call last):
...
HTTPError: 404 Not Found

The error object also has some more information in it:

>>> try:
...     client.GET('http://localhost:12345/foobar')
... except HTTPError, error:
...     pass

Let's check what's available

>>> error.code
404
>>> error.msg
'Not Found'
>>> error.fp.read()
'resource not found.'


POSTing something
~~~~~~~~~~~~~~~~~

>>> response = client.POST('http://localhost:12345/network/post','test me')
>>> response.body
'returned: test me'




