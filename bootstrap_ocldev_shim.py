"""
Lazy compatibility shim for ocldev top-level imports.

When third-party code does `import oclconstants` (top-level) we want that to
resolve to the installed `ocldev.oclconstants` module. This module inserts
lazy proxy modules into `sys.modules` so those imports resolve without
requiring changes to the third-party package.
"""
import sys
import importlib
import types

_NAMES = [
    'oclconstants',
    'oclcsvtojsonconverter',
    'oclexport',
    'oclfleximporter',
    'oclresourcelist',
    'oclvalidator',
]


class _LazyModule(types.ModuleType):
    def __init__(self, name, target):
        super().__init__(name)
        self.__dict__['_target_name'] = target

    def __getattr__(self, item):
        target = self.__dict__['_target_name']
        real = importlib.import_module(target)
        # Replace the proxy in sys.modules
        sys.modules[self.__name__] = real
        return getattr(real, item)


for name in _NAMES:
    top = name
    target = f'ocldev.{name}'
    if top not in sys.modules:
        sys.modules[top] = _LazyModule(top, target)


# Backwards-compatibility for legacy management commands that access
# BaseCommand.option_list (optparse). If the attribute is missing, provide
# a harmless empty tuple so older code that appends to it won't fail.
try:
    import django
    from django.core.management import base as django_base
    if not hasattr(django_base.BaseCommand, 'option_list'):
        setattr(django_base.BaseCommand, 'option_list', tuple())
except Exception:
    # If Django isn't available at import-time, skip this gracefully.
    pass
