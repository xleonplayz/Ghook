"""
G-Hook: Zentrale Schnittstelle für Hook-Aufrufe.
"""

from .hook_manager import GHook

# Erstelle eine globale Instanz von GHook, die das globale Projektverzeichnis verwendet.
_instance = GHook()

# Exponiere die Funktion 'muck' auf Package-Ebene:
muck = _instance.muck
