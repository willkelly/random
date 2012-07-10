#!/usr/bin/python

import argparse
import json
import sys
from copy import copy


def SubstituteType(s, delim='='):
    try:
        a, b = s.split("=", 1)
        return [a, json.loads(b)]
    except:
        raise TypeError("No %s to split on" % delim)


def JsonFileType(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        raise TypeError("Not a json file")


def nested_sub(key, data, replace):
    if key == "/" or key == "":
        return replace
    indexes = key.strip("/").split("/")
    r = copy(data)
    root = r
    i, indexes = indexes[0], indexes[1:]
    while(len(indexes) > 0 and indexes[0] != ""):
        try:
            root = root["%s" % i]
        except (TypeError, ValueError, KeyError):
            i = int(i)
            root = root[i]
        i, indexes = indexes[0], indexes[1:]
    try:
        root[i] = replace
    except TypeError:
        root[int(i)] = replace
    return r


def nested_del(key, data):
    if key == "/" or key == "":
        return None
    indexes = key.strip("/").split("/")
    r = copy(data)
    root = r
    i, indexes = indexes[0], indexes[1:]
    while(len(indexes) > 0 and indexes[0] != ""):
        try:
            root = root["%s" % i]
        except (TypeError, ValueError, KeyError):
            i = int(i)
            root = root[i]
        i, indexes = indexes[0], indexes[1:]
    try:
        del root[i]
    except TypeError:
        del root[int(i)]
    return r


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


def substitute(data, root, sub):
    return nested_sub(root, data, sub)


def delete(root, data):
    return nested_del(data, root)


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
    parser.add_argument('file', action='store',
                        metavar='file',
                        type=JsonFileType)
    args = parser.parse_args()
    if not args.ops:
        parser.print_help()
        sys.exit(1)
    if not args.file:
        args.file = JsonFileType("/dev/stdin")

    r = args.file
    for op in args.ops:
        f, fargs = op[0], [r]
        fargs.extend(op[1:])
        r = f(*fargs)
    else:
        print json.dumps(r)

if __name__ == '__main__':
    main()
