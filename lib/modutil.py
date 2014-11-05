from functools import lru_cache

from typecheck import typecheck

import networkx as nx


@typecheck
def shorten(mod_name: str, length: int=2) -> str:
    return ".".join(mod_name.split(".")[:length])


@lru_cache(maxsize=4095)
@typecheck
def levenshtein_distance(s: str, t: str) -> int:
    if not s:
        return len(t)
    if not t:
        return len(s)
    if s[0] == t[0]:
        return levenshtein_distance(s[1:], t[1:])
    l1 = levenshtein_distance(s, t[1:])
    l2 = levenshtein_distance(s[1:], t)
    l3 = levenshtein_distance(s[1:], t[1:])
    return 1 + min(l1, l2, l3)


@typecheck
def make_colors(graph: nx.Graph) -> map:
    names = graph.nodes()
    longest = max(names)
    raw = [levenshtein_distance(x, longest) for x in names]
    largest_raw = max(raw)
    degrees = [graph.degree(x) for x in graph]
    largest_degrees = max(degrees)
    return map(lambda x, y: x + y,
               [int(10 * x/largest_degrees) for x in degrees],
               [10 * x/largest_raw for x in raw])
