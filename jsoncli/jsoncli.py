#!/usr/bin/python

import argparse
import json
import sys
from functools import partial
from copy import copy
import collections


class OpType(object):
    def __init__(self, op, conversion=lambda x: x):
        self.op = op
        self.conversion = conversion

    def __call__(self, d):
        r = [self.op]
        nd = self.conversion(d)
        if type(nd) == list or type(nd) == tuple:
            r.extend(nd)
        else:
            r.append(nd)
        return r


def SubstituteType(s, delim='='):
    try:
        a, b = s.split(delim, 1)
        return [a, json.loads(b)]
    except:
        raise TypeError("Not in key=valid_json format")


def JsonFileType(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        raise TypeError("Not a json file")


def nested_op(key, data, f=lambda x, i: x[i], ret=None):
    if key == '/' or key == '':
        return ret
    indexes = key.strip("/").split("/")
    r = copy(data)
    root = r
    i, indexes = indexes[0], indexes[1:]
    while(len(indexes) > 0 and indexes[0] != ""):
        if isinstance(root, collections.Sequence):
            i = int(i)
        root = root[i]
        i, indexes = indexes[0], indexes[1:]
    if isinstance(root, collections.Sequence):
        i = int(i)
    f(root, i)
    return r


def substitute(data, key, replace):
    def replaces(root, i):
        root[i] = replace
    return nested_op(key, data, f=replaces, ret=data)


def delete(data, key):
    def deleted(root, i):
        del root[i]
    return nested_op(key, data, f=deleted, ret=None)


def main():
    parser = argparse.ArgumentParser(description="Parse and manipulate json, "
                                     "specify one or more substitute "
                                     "and delete")
    parser.add_argument('--substitute', '-s', action='append',
                        type=OpType(substitute, SubstituteType),
                        help='/path/to/json/root={"valid": "json"}',
                        dest="ops")
    parser.add_argument('--delete', '-d',
                        action='append',
                        help='/path/to/json/root',
                        dest="ops", type=OpType(delete))
    parser.add_argument('--bail', '-b',
                        action='store_true',
                        default=False)
    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        default=False)
    parser.add_argument('file', action='store',
                        metavar='file',
                        type=JsonFileType)
    args = parser.parse_args()

    if not args.file:
        args.file = JsonFileType("/dev/stdin")

    r = args.file
    for op in args.ops:
        try:
            f, fargs = op[0], [r]
            fargs.extend(op[1:])
            r = f(*fargs)
        except (KeyError, IndexError):
            if not args.quiet:
                sys.stderr.write("Failed to apply %s\n" % op)
            if args.bail:
                sys.exit(1)
    print json.dumps(r)

if __name__ == '__main__':
    main()
