#  Copyright (c) 2018 Victor Porton,
#  XML Boiler - http://freesoft.portonvictor.org
#
#  This file is part of XML Boiler.
#
#  XML Boiler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


# Directed graph with at most one edge between vertices
class BinaryRelation(object):
    def __init__(self, adj=None):
        """
        :param adj: a dict from vertice to vertex set
        """
        self.adj = dict() if adj is None else adj

    def __eq__(self, other):
        return self.adj == other.adj

    def __hash__(self):
        return hash(self.adj)

    def add_edge(self, src, dst):
        value = self.adj.get(src, None)
        if value is None:
            self.adj[src] = {dst}
        else:
            value.append(dst)

    def adjanced(self, src, dst):
        s = self.adj.get(src, None)
        if s is None:
            return False
        return dst in s

    def reverse(self):
        result = BinaryRelation()
        for key, value in self.adj.items():
            for y in value:
                result.add_edge(y, key)
        return result


def compose(b, a):
    """
    Note order of arguments!
    """
    result = BinaryRelation()
    for x, s in a.adj.items():
        for y in s:
            s2 = b.adj.get(y, None)
            if s2 is not None:
                for z in s2:
                    result.add_edge(x, z)
    return result


def square(graph):
    return compose(graph, graph)


def union(a, b):
    source = set()
    source |= a.adj.keys()
    source |= b.adj.keys()
    adj = dict()
    for x in source:
        setA = a.adj.get(x, None)
        setB = b.adj.get(x, None)
        if a is not None or b is not None:
            s = dict()
            if not a is None:
                s |= setA
            if not b is None:
                s |= setB
            adj[x] = s
    return BinaryRelation(adj)
