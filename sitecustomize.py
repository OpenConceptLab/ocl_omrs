"""
sitecustomize imported automatically by Python at startup when on sys.path.
It will import our bootstrap shim so top-level names like `oclconstants` are
available (resolved lazily to `ocldev.*`) before other imports occur.
"""
try:
    import bootstrap_ocldev_shim  # ensure lazy proxies are installed early
except Exception:
    # If the shim isn't present (e.g., running in a different environment),
    # silently continue — imports will fall back to installed packages.
    pass
