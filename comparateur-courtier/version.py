# -*- coding: utf-8 -*-
"""Version de l'application — source unique de vérité.

Bumper ce numéro à chaque release, puis :
  1. python build_exe.py          (rebuild l'exe générique)
  2. gh release create vX.Y.Z ...  (avec dist/ComparateurCourtier.exe en asset)

Le numéro est embarqué dans l'exe (import) et sert à la vérification de MAJ.
"""
APP_VERSION = "1.2.1"
