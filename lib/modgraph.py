#!/usr/bin/env python
from collections import Counter, OrderedDict
from functools import lru_cache
import itertools
from modulefinder import Module, ModuleFinder
import sys

import networkx as nx

import matplotlib.pyplot as plt


matplotlib_groupings = {
    "backend layer": ["matplotlib.backend",
                      "matplotlib.blocking",
                      "matplotlib.dviread",
                      "matplotlib.mathtext",
                      "matplotlib.texmanager",
                      "matplotlib.type1font",
                      "matplotlib.widgets"],
    "artist layer": ["matplotlib.afm",
                     "matplotlib.animation",
                     "matplotlib.artist",
                     "matplotlib.ax",
                     "matplotlib.container",
                     "matplotlib.contour",
                     "matplotlib.figure",
                     "matplotlib.gridspec",
                     "matplotlib.hatch",
                     "matplotlib.image",
                     "matplotlib.legend",
                     "matplotlib.lines",
                     "matplotlib.marker",
                     "matplotlib.offset",
                     "matplotlib.patches",
                     "matplotlib.path",
                     "matplotlib.projection",
                     "matplotlib.quiver",
                     "matplotlib.sankey",
                     "matplotlib.scale",
                     "matplotlib.spines",
                     "matplotlib.stackplot",
                     "matplotlib.streamplot",
                     "matplotlib.table",
                     "matplotlib.text",
                     "matplotlib.ticker",
                     "matplotlib.tight",
                     "matplotlib.transforms",
                     "matplotlib.tri.",
                     "matplotlib.units"],
    "scripting layer": ["matplotlib.mlab",
                        "matplotlib.pylab",
                        "matplotlib.pyplot"],
    "configuration": ["matplotlib.rcsetup",
                      "matplotlib.style"],
    "utilities": ["matplotlib.bezier",
                  "matplotlib.cbook",
                  "matplotlib.cm",
                  "matplotlib.collections",
                  "matplotlib.color",
                  "matplotlib.compat",
                  "matplotlib.dates",
                  "matplotlib.delaunay",
                  "matplotlib.docstring",
                  "matplotlib.finance",
                  "matplotlib.font",
                  "matplotlib.sphinxext"]}


module_lookup = dict(list(itertools.chain(*
    [[(x, layer) for x in match]
     for (layer, match) in matplotlib_groupings.items()])))


def shorten(mod_name:str, length:int=2) -> str:
    return ".".join(mod_name.split(".")[:length])


@lru_cache(maxsize=4095)
def levenshtein_distance(s:str, t:str) -> int:
    if not s: return len(t)
    if not t: return len(s)
    if s[0] == t[0]: return levenshtein_distance(s[1:], t[1:])
    l1 = levenshtein_distance(s, t[1:])
    l2 = levenshtein_distance(s[1:], t)
    l3 = levenshtein_distance(s[1:], t[1:])
    return 1 + min(l1, l2, l3)


def make_colors(graph:list) -> list:
    names = graph.nodes()
    longest = max(names)
    raw = [levenshtein_distance(x, longest) for x in names]
    largest_raw = max(raw)
    degrees = [graph.degree(x) for x in graph]
    largest_degrees = max(degrees)
    return map(lambda x, y: x + y,
               [int(10 * x/largest_degrees) for x in degrees],
               [10 * x/largest_raw for x in raw])


class CustomFinder(ModuleFinder):
    def __init__(self, root:str, include:list, layout:str, graph_class:type,
                 mode:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cf_root = root
        self.debug = False
        self.cf_include = include
        self.cf_layout = layout
        self.cf_graph_class = graph_class
        self.cf_mode = mode
        self.cf_imports = OrderedDict()
        self.cf_weights = Counter()
        self.cf_node_multiplier = 1
        self.cf_exclude = ["matplotlib._", "ft2font", "ttconv"]

    def matches(self, name:str) -> bool:
        if ((True in [name.startswith(x) for x in self.cf_include])
            and
            (True not in [name.startswith(x) for x in self.cf_exclude])):
            return True
        return False

    def import_hook(self, name:str, caller:Module=None, fromlist:list=None,
                    level:int=-1) -> Module:
        if self.matches(name):
            if caller:
                if self.debug:
                    print(caller.__name__, " -> ", name)
                self.cf_weights[name] += 1
                self.cf_imports[(caller.__name__, name)] = 1
            super().import_hook(name, caller, fromlist, level)

    def relations(self) -> list:
        return [(key, val, {"weight": self.cf_weights[val]})
                for (key, val) in self.cf_imports.keys()]

    def simple_relations(self) -> list:
        new_weights = Counter()
        relations = []
        for (key, val) in self.cf_imports.keys():
            (short_key, short_val) = (shorten(key), shorten(val))
            new_weights[short_val] += self.cf_weights[val]
            relations.append((short_key, short_val))
        self.cf_weights = new_weights
        return [(key, val, {"weight": self.cf_weights[val]})
                for (key, val) in relations]

    def as_dict(self):
        return [dict([x]) for x in self.cf_imports.keys()]

    def graph(self) -> nx.Graph:
        if self.cf_mode == "simple":
            data = self.simple_relations()
        elif self.cf_mode == "full":
            data = self.relations()
        elif self.cf_mode == "structured":
            data = self.structured_relations()
        else:
            raise Exception("Undefined mode.")
        return self.cf_graph_class(data)

    def save(self) -> None:
        plt.figure(figsize=(35,35))
        if self.cf_mode == "simple":
            self.cf_node_multiplier = 10
        elif self.cf_mode == "full":
            self.cf_node_multiplier = 200
        graph = self.graph()
        node_sizes = [self.cf_node_multiplier * self.cf_weights[x]
                     for x in graph]
        node_colors = [float(x) for x in make_colors(graph)]
        if self.debug:
            print("\nDegrees: ", [graph.degree(x) for x in graph])
            print("\nShorten: ", [shorten(x) for x in graph])
            print("\nColors: ", [int(x) for x in make_colors(graph)])
        pos = nx.graphviz_layout(graph, prog=self.cf_layout, root=self.cf_root)
        nx.draw(graph, pos, node_size=node_sizes, node_color=node_colors,
                with_labels=True, alpha=0.5)
        plt.savefig("modgraph.png")

    def render(self, layout:str="", labels:bool=True, mode:str="") -> None:
        if layout:
            self.cf_layout = layout
        if mode:
            self.cf_mode = mode
        plt.figure(figsize=(12,12))
        if self.cf_mode == "simple":
            self.cf_node_multiplier = 0.7
        elif self.cf_mode == "full":
            self.cf_node_multiplier = 20
        graph = self.graph()
        node_sizes = [self.cf_node_multiplier * self.cf_weights[x]
                     for x in graph]
        node_colors = [float(x) for x in make_colors(graph)]
        pos = nx.graphviz_layout(graph, prog=self.cf_layout, root=self.cf_root)
        nx.draw(graph, pos, node_size=node_sizes, node_color=node_colors,
                with_labels=labels, alpha=0.5, edge_color="#666666")
