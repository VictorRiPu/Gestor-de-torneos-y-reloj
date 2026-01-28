from __future__ import annotations

import sys
from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1] / "Rivera_Puebla_Victor_appTorneoFutbol"
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


from Views.components.reloj_widget import *  # noqa: F401,F403

