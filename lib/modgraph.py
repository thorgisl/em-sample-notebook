from collections import Counter

from typecheck import typecheck
import typecheck as tc

import networkx as nx

import matplotlib.pyplot as plt

from modarch import get_group
from modfind import CustomFinder
from modutil import make_colors, shorten


class ModGrapher:
    def __init__(self, source: str="", include: list=None, exclude: list=None,
                 root: str="__main__", layout: str="dot",
                 graph_class: nx.Graph=nx.Graph, mode: str="full",
                 size: int=12, labels: bool=True, font_size: int=12,
                 *args, **kwargs):
        self.source = source
        include = include or ["matpl", "mpl_"]
        exclude = exclude or ["matplotlib._",
                              "matplotlib.ft2font",
                              "matplotlib.ttconv"]
        self.finder = CustomFinder(include, exclude)
        self.root = root
        self.debug = False
        self.layout = layout
        self.graph_class = graph_class
        self.mode = mode
        self.weights = Counter()
        self.node_multiplier = 1
        self.size = size
        self.labels = labels
        self.font_size = font_size

    @typecheck
    def get_imports(self) -> list:
        return [(key, val) for (key, val) in self.finder.cf_imports.keys()
                if (key != "matplotlib" and val != "matplotlib")]

    @typecheck
    def relations(self) -> list:
        self.weights = self.finder.cf_weights
        return [(key, val, {"weight": self.weights[val] or 1})
                for (key, val) in self.get_imports()]

    @typecheck
    def simple_relations(self) -> list:
        new_weights = Counter()
        relations = []
        for (key, val) in self.get_imports():
            (short_key, short_val) = (shorten(key), shorten(val))
            new_weights[short_val] += self.finder.cf_weights[val]
            relations.append((short_key, short_val))
        self.weights = new_weights
        return [(key, val, {"weight": self.weights[val] or 1})
                for (key, val) in relations]

    @typecheck
    def reduced_relations(self) -> list:
        new_weights = Counter()
        relations = []
        for (key, val) in self.get_imports():
            (short_key, short_val) = (get_group(key), get_group(val))
            new_weights[short_val] += self.finder.cf_weights[val]
            relations.append((short_key, short_val))
        self.weights = new_weights
        return [(key, val, {"weight": self.weights[val] or 1})
                for (key, val) in set(relations)]

    @typecheck
    def simple_struct_relations(self) -> list:
        new_weights = Counter()
        relations = []
        for (key, val) in self.get_imports():
            (short_key, short_val) = (shorten(key), shorten(val))
            (key_group, val_group) = (get_group(key), get_group(val))
            new_weights[short_val] += self.finder.cf_weights[val]
            new_weights[key_group] += self.finder.cf_weights[val]
            if key_group == val_group:
                relations.extend([(short_key, key_group),
                                  (short_val, val_group)])
            else:
                relations.append((key_group, val_group))
        self.weights = new_weights
        return [(key, val, {"weight": self.weights[val] or 1})
                for (key, val) in relations]

    @typecheck
    def struct_relations(self) -> list:
        new_weights = self.finder.cf_weights
        relations = []
        for (key, val) in self.get_imports():
            (key_group, val_group) = (get_group(key), get_group(val))
            new_weights[key_group] += self.finder.cf_weights[val]
            if key_group == val_group:
                relations.extend([(key, key_group),
                                  (val, val_group)])
            else:
                relations.append((key_group, val_group))
        self.weights = new_weights
        return [(key, val, {"weight": self.weights[val] or 1})
                for (key, val) in relations]

    @typecheck
    def as_dict(self) -> list:
        return [dict([x]) for x in self.get_imports()]

    @typecheck
    def graph(self) -> nx.Graph:
        if self.mode == "simple":
            data = self.simple_relations()
        elif self.mode == "full":
            data = self.relations()
        elif self.mode == "reduced-structure":
            data = self.reduced_relations()
        elif self.mode == "simple-structure":
            data = self.simple_struct_relations()
        elif self.mode == "full-structure":
            data = self.struct_relations()
        else:
            raise Exception("Undefined mode.")
        if self.debug:
            print("Graph data: ", data)
        return self.graph_class(data)

    @typecheck
    def render(self, layout: str="", labels: tc.optional(bool)=None,
               mode: str="", source: str="", size: int=0,
               font_size: tc.optional(int)=None):
        if layout:
            self.layout = layout
        if labels is not None:
            self.labels = labels
        if mode:
            self.mode = mode
        if source:
            self.source = source
            self.weights = Counter()
        if size:
            self.size = size
        if font_size is not None:
            self.font_size = font_size
        if self.mode == "simple":
            self.node_multiplier = 0.7
        elif self.mode == "full":
            self.node_multiplier = 20
        elif self.mode == "reduced-structure":
            self.node_multiplier = 4
        elif self.mode == "simple-structure":
            self.node_multiplier = 4
            self.font_size = 10
        elif self.mode == "full-structure":
            self.node_multiplier = 6
            self.font_size = 8
        if not self.weights:
            self.finder.run_script(self.source)
        self.draw()

    @typecheck
    def draw(self):
        plt.figure(figsize=(self.size, self.size))
        graph = self.graph()
        node_sizes = [self.node_multiplier * (self.weights[x] or 1)
                      for x in graph]
        node_colors = [float(x) for x in make_colors(graph)]
        if self.debug:
            print("Graph nodes: ", graph.nodes())
            print("Node sizes: ", node_sizes)
            print("Node colors: ", node_colors)
            print("Graph nodes size: ", len(graph.nodes()))
            print("Node sizes size: ", len(node_sizes))
            print("Node colors size: ", len(node_colors))
        pos = nx.graphviz_layout(graph, prog=self.layout, root=self.root)
        nx.draw(graph, pos, node_size=node_sizes, node_color=node_colors,
                with_labels=self.labels, alpha=0.5, edge_color="#666666",
                font_size=self.font_size)


__all__ = ["ModGrapher"]
