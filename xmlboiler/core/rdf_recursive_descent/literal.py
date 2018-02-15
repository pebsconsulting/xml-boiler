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

from rdflib import Literal, XSD, URIRef

from xmlboiler.core.rdf_recursive_descent.base import *


class IRILiteral(NodeParserWithError):
    def parse(self, parse_context, graph, node):
        if node in URIRef:
            return node
        else:
            self.throw(lambda: self.parse_context.translate("Node {node} should be an IRI.").format(node=node))


class StringLiteral(NodeParserWithError):
    def parse(self, parse_context, graph, node):
        # TODO: xsd:normalizedString support
        if node not in Literal or node.datatype != XSD.string:
            self.throw(lambda: self.parse_context.translate("Node {node} is not a string literal.").format(node=node))
        return str(node)


class BooleanLiteral(NodeParserWithError):
    def parse(self, parse_context, graph, node):
        if node in Literal and node.datatype == XSD.boolean:
            if node.value in ("0", "false"):
                return False
            if node.value in ("1", "true"):
                return True
        self.throw(lambda: self.parse_context.translate("Node {node} is not a boolean literal.").format(node=node))


class IntegerLiteral(NodeParserWithError):
    def parse(self, parse_context, graph, node):
        if node in Literal and node.datatype == XSD.integer and \
                len(node.value) != 0 and node.value[0] != ' ' and node.value[-1] != ' ':
            try:
                return int(node.value)
            except ValueError:
                pass
        self.throw(lambda: self.parse_context.translate("Node {node} is not an integer literal.").format(node=node))


class FloatLiteral(NodeParserWithError):
    def parse(self, parse_context, graph, node):
        if node in Literal and node.datatype in (XSD.integer, XSD.float, XSD.double, XSD.decimal) and \
                len(node.value) != 0 and node.value[0] != ' ' and node.value[-1] != ' ':
            try:
                return float(node.value)
            except ValueError:
                pass
        self.throw(lambda: self.parse_context.translate("Node {node} is not a float literal.").format(node=node))