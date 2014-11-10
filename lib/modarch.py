import itertools

from typecheck import typecheck


debug = False
top_level_group = "top level"
unknown_group = "unknown"
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
                  "matplotlib.sphinxext",
                  "mpl_tool"]}


reverse_matplotlib_groupings = dict(list(
    itertools.chain(*[[(x, group) for x in mod_part]
                      for (group, mod_part) in matplotlib_groupings.items()])))


@typecheck
def get_group(mod_name: str) -> str:
    mod_name = mod_name.strip()
    if mod_name == "__main__":
        return mod_name
    if mod_name == "matplotlib":
        return top_level_group
    if mod_name in reverse_matplotlib_groupings:
        if debug:
            print("[X] Found quick match for '{}'!".format(mod_name))
        return reverse_matplotlib_groupings[mod_name]
    for (mod_part, group) in reverse_matplotlib_groupings.items():
        if mod_name.startswith(mod_part):
            if debug:
                print("[-] Found slow match for '{}'...".format(mod_name))
            return group
    if debug:
        print("[ ] Cound't find match for '{}' ...".format(mod_name))
    return unknown_group


__all__ = ["matplotlib_groupings", "reverse_matplotlib_groupings",
           "get_group"]
del typecheck, itertools
