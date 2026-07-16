# -*- coding: utf-8 -*-
"""Version de l'application â€” source unique de vÃ©ritÃ©.

Bumper ce numÃ©ro Ã  chaque release, puis :
  1. python build_exe.py          (rebuild l'exe gÃ©nÃ©rique)
  2. gh release create vX.Y.Z ...  (avec dist/ComparateurCourtier.exe en asset)

Le numÃ©ro est embarquÃ© dans l'exe (import) et sert Ã  la vÃ©rification de MAJ.
"""
APP_VERSION = "1.2.2"
