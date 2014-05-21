
from statement import *

"""This file contains mappings from class ID numbers to class names, and vice versa."""

ID_TO_STATEMENT = {
    0 : "Nil",
    1 : "Number",
    2 : "Function"
}

STATEMENT_TO_ID = {}
for id, stmt in ID_TO_STATEMENT.iteritems():
    STATEMENT_TO_ID[stmt] = id


def statement_class_from_id(id):
    return globals()[ID_TO_STATEMENT[id]]

def id_from_statement_class(kls):
    return STATEMENT_TO_ID[kls.__name__]

