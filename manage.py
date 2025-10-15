#!/usr/bin/env python3
import os
import sys
# Ensure the ocldev -> top-level ocl* lazy shim is installed early so
# modules that do `import oclconstants` resolve correctly to `ocldev.oclconstants`.
try:
    import bootstrap_ocldev_shim  # noqa: F401
except Exception:
    # best-effort: if the shim isn't present in the source tree we'll fall back
    # to relying on the installed package. Keep failures silent here.
    pass

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omrs.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
