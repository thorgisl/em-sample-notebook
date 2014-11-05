from collections import Counter, OrderedDict
import itertools
from modulefinder import Module, ModuleFinder

from typecheck import typecheck
import typecheck as tc

import networkx as nx

import matplotlib.pyplot as plt

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


class CustomFinder(ModuleFinder):
    def __init__(self, include: list=None, exclude: list=None,
                 root: str="__main__", layout: str="dot",
                 graph_class: nx.Graph=nx.Graph, mode: str="full",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cf_root = root
        self.debug = False
        self.cf_include = include or ["matpl", "mpl"]
        self.cf_exclude = exclude or ["matplotlib._", "ft2font", "ttconv"]
        self.cf_layout = layout
        self.cf_graph_class = graph_class
        self.cf_mode = mode
        self.cf_imports = OrderedDict()
        self.cf_weights = Counter()
        self.cf_node_multiplier = 1

    @typecheck
    def matches(self, name: str) -> bool:
        include = True in [name.startswith(x) for x in self.cf_include]
        exclude = True in [name.startswith(x) for x in self.cf_exclude]
        if include and not exclude:
            return True
        return False

    @typecheck
    def import_hook(self, name: str, caller: tc.optional(Module)=None,
                    fromlist: tc.optional(list)=None,
                    level: int=-1) -> tc.optional(Module):
        if self.matches(name):
            if caller:
                if self.debug:
                    print(caller.__name__, " -> ", name)
                self.cf_weights[name] += 1
                self.cf_imports[(caller.__name__, name)] = 1
            super().import_hook(name, caller, fromlist, level)

    @typecheck
    def relations(self) -> list:
        return [(key, val, {"weight": self.cf_weights[val]})
                for (key, val) in self.cf_imports.keys()]

    @typecheck
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

    @typecheck
    def as_dict(self) -> list:
        return [dict([x]) for x in self.cf_imports.keys()]

    @typecheck
    def graph(self) -> nx.Graph:
        if self.cf_mode == "simple":
            data = self.simple_relations()
        elif self.cf_mode == "full":
            data = self.relations()
        elif self.cf_mode == "reduced-structure":
            data = self.reduced_relations()
        elif self.cf_mode == "simple-structure":
            pass
        elif self.cf_mode == "full-structure":
            pass
        else:
            raise Exception("Undefined mode.")
        return self.cf_graph_class(data)

    @typecheck
    def render(self, layout: str="", labels: bool=True,
               mode: str="") -> tc.optional(None):
        if layout:
            self.cf_layout = layout
        if mode:
            self.cf_mode = mode
        if self.cf_mode == "simple":
            self.cf_node_multiplier = 0.7
        elif self.cf_mode == "full":
            self.cf_node_multiplier = 20
        self.draw(labels)
        return None

    @typecheck
    def draw(self, labels: bool) -> tc.optional(None):
        plt.figure(figsize=(12, 12))
        graph = self.graph()
        node_sizes = [self.cf_node_multiplier * self.cf_weights[x]
                      for x in graph]
        node_colors = [float(x) for x in make_colors(graph)]
        pos = nx.graphviz_layout(graph, prog=self.cf_layout, root=self.cf_root)
        nx.draw(graph, pos, node_size=node_sizes, node_color=node_colors,
                with_labels=labels, alpha=0.5, edge_color="#666666")
        return None
