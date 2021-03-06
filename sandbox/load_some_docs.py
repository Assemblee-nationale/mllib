# -*- coding: utf-8 -*-
"""
=============================================
Loading some documentation to the ML database
=============================================
"""
from __future__ import print_function, unicode_literals, absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import input
from io import StringIO
import logging
import json
import os

from mllib.documents import DocumentsService
from mllib.eval import EvalService
from mllib.utils import ResponseAdapter

logging.basicConfig(level=logging.WARNING)  # Try "INFO" then "DEBUG" for more verbosity

demo_doc_uris = []


def hit_return():
    input("\nHit [Return] to continue:")

if 'MLLIB_TEST_SERVER' not in os.environ:
    os.environ['MLLIB_TEST_SERVER'] = 'localhost:8000:admin:admin'

LOREM_IPSUM = b"""
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

# We create the document service
ds = DocumentsService.from_envvar('MLLIB_TEST_SERVER')

# We push a first document

DOC_XML = b"""
<root>
  <uid>A00</uid>
  <title>A simple XML document</title>
  <content>
  {}
  </content>
</root>
""".format(LOREM_IPSUM)

uri = "python_demo/sample1/doc1.xml"
demo_doc_uris.append(uri)
ds.document_put(StringIO(DOC_XML), uri=uri)

print("\nA new document is at {}".format(uri))
hit_return()

# We push a second document in named collections with properties

DOC_JSON = {
    'uid': 'A01',
    'title': "A simple JSON document",
    'content': LOREM_IPSUM
}
DOC_JSON = json.dumps(DOC_JSON, ensure_ascii=True)

uri = "python_demo/sample1/doc2.json"
demo_doc_uris.append(uri)
ds.document_put(StringIO(DOC_JSON), uri=uri, collection=('books', 'manuals'),
                prop={'author': 'Joe', 'status': 'draft'})

print("\nA new document is at {}".format(uri))
hit_return()

# We push a third document in some categories

uri = "python_demo/doc1.xml"
demo_doc_uris.append(uri)
ds.document_put(StringIO(DOC_XML), uri=uri, collection=['spec', 'functional'])

print("\nA new document is at {0} in categories 'spec' and 'functional'.".format(uri))
hit_return()

# Okay, let's retrieve a document which URI is known

uri = 'python_demo/sample1/doc1.xml'
print("\nWe retrieve the document stored at uri '{0}'".format(uri))
response = ds.document_get(uri=uri)
print ("-" * 79)
print(response.text)
print ("-" * 79)

# Let's retrieve several documents in one request

uris = [uri, "python_demo/sample1/doc2.json"]
print("We retrieve 2 documents '{0[0]}' and '{0[1]}' in one request".format(uris))
response = ds.document_get(uri=uris)
assert isinstance(response, ResponseAdapter)

for i, (headers, document) in enumerate(response.iter_parts()):
    print ("=" * 79)
    print("Document '{0}'".format(uris[i]))
    print("Headers:")
    print ("-" * 79)
    print(headers)
    print ("-" * 79)
    print("Body:")
    print ("-" * 79)
    print(document)

# Let's evaluate some information from the server

ADDITION_XQY = b"""
xquery version "1.0-ml";
declare variable $value1 as xs:integer external;
declare variable $value2 as xs:integer external;
fn:sum(($value1, $value2));
"""

print("\nTesting server side XQuery evaluation")

def ml_int_addition(value1, value2):
    """A simple and useless server side operation
    """
    es = EvalService.from_envvar('MLLIB_TEST_SERVER')
    response = es.eval_post(xquery=ADDITION_XQY, vars={'value1': value1, 'value2': value2})
    headers, document = next(response.iter_parts())
    assert headers['X-Primitive'] == 'integer'
    return int(document)

result = ml_int_addition(11, 15)
print(result)
assert result == 26
print("\nYeah ML says 11 + 15 is 26")

# Database cleanup

print("\nWe will now delete all documents created for this demo.")
hit_return()

# Before ML 8.0.3
# for uri in demo_doc_uris:
#     print("Deleting {}".format(uri))
#     ds.document_delete(uri=uri)

# ML 8.0.3 and later we can delete 2+ documents in one single request
ds.document_delete(uri=demo_doc_uris)
