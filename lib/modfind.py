from collections import Counter, OrderedDict
from modulefinder import Module, ModuleFinder

from typecheck import typecheck
import typecheck as tc


class CustomFinder(ModuleFinder):
    def __init__(self, include: list=None, exclude: list=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = False
        self.cf_include = include or ["matpl", "mpl"]
        self.cf_exclude = exclude or ["matplotlib._", "ft2font", "ttconv"]
        self.cf_imports = OrderedDict()
        self.cf_weights = Counter()

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


__all__ = ["CustomFinder"]
del Module, ModuleFinder, typecheck, tc
