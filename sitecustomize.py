"""Observer startup corrections.

Python imports ``sitecustomize`` automatically when this repository is on
``sys.path``. Keeping the release correction here ensures command-line tests and
local development use the same canonical-return implementation as the desktop
launcher.
"""

import observer_hotfix  # noqa: F401
