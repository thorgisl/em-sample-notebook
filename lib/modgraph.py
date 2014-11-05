#!/usr/bin/env python
from collections import Counter, OrderedDict
from functools import lru_cache
from modulefinder import Module, ModuleFinder
import sys

import networkx as nx

import matplotlib.pyplot as plt


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
        self.cf_include = include
        self.cf_layout = layout
        self.cf_graph_class = graph_class
        self.cf_mode = mode
        self.cf_imports = OrderedDict()
        self.cf_weights = Counter()
        self.cf_node_multiplier = 1

    def matches(self, name:str) -> bool:
        if True in [name.startswith(x) for x in self.cf_include]:
            return True
        return False

    def import_hook(self, name:str, caller:Module=None, fromlist:list=None,
                    level:int=-1) -> Module:
        if self.matches(name):
            if caller:
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
            self.cf_node_multiplier =10
        elif self.cf_mode == "full":
            data = self.relations()
            self.cf_node_multiplier = 200
        elif self.cf_mode == "structured":
            data = self.structured_relations()
        else:
            raise Exception("Undefined mode.")
        return self.cf_graph_class(data)

    def render(self) -> None:
        plt.figure(figsize=(35,35))
        graph = self.graph()
        node_sizes = [self.cf_node_multiplier * self.cf_weights[x]
                     for x in graph]
        node_colors = [float(x) for x in make_colors(graph)]
        print("\nDegrees: ", [graph.degree(x) for x in graph])
        print("\nShorten: ", [shorten(x) for x in graph])
        print("\nColors: ", [int(x) for x in make_colors(graph)])
        pos = nx.graphviz_layout(graph, prog=self.cf_layout, root=self.cf_root)
        nx.draw(graph, pos, node_size=node_sizes, node_color=node_colors,
                with_labels=True, alpha=0.5)
        plt.savefig("modgraph.png")


def usage(scriptname:str) -> None:
    print("Usage:\n\t{} filename [layout [mode]]\n".format(scriptname))


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        usage(args[0])
        exit(1)
    if len(args) >= 3:
        layout = args[2]
    else:
        layout = "dot"
    if len(args) >= 4:
        mode = args[3]
    else:
        mode = "full"
    finder = CustomFinder("__main__", ["matpl", "mpl"], layout, nx.Graph, mode)
    finder.run_script(sys.argv[1])
    print("\nModules: ", sorted(finder.modules.keys()))
    print("\nAs dict: ", finder.as_dict())
    print("\nWeights: ", finder.cf_weights.items())
    finder.render()
