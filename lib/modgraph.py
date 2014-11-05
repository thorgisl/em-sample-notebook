from collections import Counter
import itertools

from typecheck import typecheck
import typecheck as tc

import networkx as nx

import matplotlib.pyplot as plt

from modfind import CustomFinder
from modutil import make_colors, shorten


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


module_lookup = dict(list(
    itertools.chain(*[[(x, layer) for x in match]
                      for (layer, match) in matplotlib_groupings.items()])))


class ModGrapher:
    def __init__(self, source: str="", include: list=None, exclude: list=None,
                 root: str="__main__", layout: str="dot",
                 graph_class: nx.Graph=nx.Graph, mode: str="full",
                 *args, **kwargs):
        self.source = source
        include = include or ["matpl", "mpl"]
        exclude = exclude or ["matplotlib._", "ft2font", "ttconv"]
        self.finder = CustomFinder(include, exclude)
        self.root = root
        self.debug = False
        self.layout = layout
        self.graph_class = graph_class
        self.mode = mode
        self.weights = Counter()
        self.node_multiplier = 1

    @typecheck
    def relations(self) -> list:
        self.weights = self.finder.cf_weights
        return [(key, val, {"weight": self.weights[val]})
                for (key, val) in self.finder.cf_imports.keys()]

    @typecheck
    def simple_relations(self) -> list:
        new_weights = Counter()
        relations = []
        for (key, val) in self.finder.cf_imports.keys():
            (short_key, short_val) = (shorten(key), shorten(val))
            new_weights[short_val] += self.finder.cf_weights[val]
            relations.append((short_key, short_val))
        self.weights = new_weights
        return [(key, val, {"weight": self.weights[val]})
                for (key, val) in relations]

    @typecheck
    def as_dict(self) -> list:
        return [dict([x]) for x in self.finder.cf_imports.keys()]

    @typecheck
    def graph(self) -> nx.Graph:
        if self.mode == "simple":
            data = self.simple_relations()
        elif self.mode == "full":
            data = self.relations()
        elif self.mode == "reduced-structure":
            data = self.reduced_relations()
        elif self.mode == "simple-structure":
            pass
        elif self.mode == "full-structure":
            pass
        else:
            raise Exception("Undefined mode.")
        return self.graph_class(data)

    @typecheck
    def render(self, layout: str="", labels: bool=True,
               mode: str="", source: str="") -> tc.optional(None):
        if layout:
            self.layout = layout
        if mode:
            self.mode = mode
        if source:
            self.source = source
            self.weights = Counter()
        if self.mode == "simple":
            self.node_multiplier = 0.7
        elif self.mode == "full":
            self.node_multiplier = 20
        if not self.weights:
            self.finder.run_script(self.source)
        self.draw(labels)
        return None

    @typecheck
    def draw(self, labels: bool) -> tc.optional(None):
        plt.figure(figsize=(12, 12))
        graph = self.graph()
        node_sizes = [self.node_multiplier * self.weights[x]
                      for x in graph]
        node_colors = [float(x) for x in make_colors(graph)]
        pos = nx.graphviz_layout(graph, prog=self.layout, root=self.root)
        nx.draw(graph, pos, node_size=node_sizes, node_color=node_colors,
                with_labels=labels, alpha=0.5, edge_color="#666666")
        return None
