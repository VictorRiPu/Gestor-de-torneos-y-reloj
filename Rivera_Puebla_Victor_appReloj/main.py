from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

from reloj_widget import RelojDigital


def _parse_language_argument(argv: list[str]) -> tuple[Optional[str], list[str]]:
    language = None
    cleaned = [argv[0]]
    for arg in argv[1:]:
        if arg.startswith("--lang="):
            language = arg.split("=", 1)[1].strip() or None
        else:
            cleaned.append(arg)
    return language, cleaned


def main() -> int:
    language, qt_args = _parse_language_argument(sys.argv)
    app = QApplication(qt_args)

    reloj = RelojDigital()
    if language:
        reloj.setLanguage(language)
    reloj.setWindowTitle(reloj.tr("Digital Clock"))
    reloj.resize(420, 240)
    reloj.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
