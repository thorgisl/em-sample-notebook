from functools import lru_cache
import subprocess

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


@typecheck
def has_excluded(item: str) -> bool:
    exclude = [".dylibs", "__pycache__", ".so", "__.py", ".nib", ".", ".."]
    if True in [item.endswith(x) for x in exclude]:
        return True
    return False


@typecheck
def output_filter(results: list) -> str:
    return "\n".join([x for x in results if not has_excluded(x)])


@typecheck
def run_cmd(*command):
    return subprocess.check_output(
        " ".join(command),
        shell=True,
        universal_newlines=True).splitlines()


@typecheck
def ls(*args):
    command = ["ls -al"] + list(args)
    print(output_filter(run_cmd(*command)))


@typecheck
def rm(*args):
    command = ["rm"] + list(args)
    run_cmd(*command)


__all__ = ["shorten", "make_colors", "ls", "rm"]
del lru_cache, typecheck, nx
