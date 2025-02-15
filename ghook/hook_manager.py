import json
import importlib.util
from pathlib import Path
import os

# Globaler Standardpfad: Wird als Umgebungsvariable überschrieben,
# oder liegt standardmäßig im Home-Verzeichnis
DEFAULT_PROJECT_DIR = Path(os.environ.get("GHOOK_PROJECT_DIR", Path.home() / ".ghook_project"))

class GHook:
    def __init__(self, project_dir=None):
        """
        Initialisiert G-Hook.
        Standardmäßig wird das globale Projektverzeichnis verwendet,
        das über die Umgebungsvariable GHOOK_PROJECT_DIR gesetzt werden kann
        oder im Home-Verzeichnis unter ~/.ghook_project liegt.
        """
        if project_dir is None:
            self.project_dir = DEFAULT_PROJECT_DIR
        else:
            self.project_dir = Path(project_dir)
            
        self.config_file = self.project_dir / "config.json"
        self.hooks_folder = self.project_dir / "hooks"
        print(f"[DEBUG] Globales Projektverzeichnis: {self.project_dir}")
        print(f"[DEBUG] Suche nach config.json unter: {self.config_file}")
        self.hooks = self._load_config()

    def _load_config(self):
        """
        Lädt die Konfiguration aus der config.json.
        """
        if not self.config_file.exists():
            print(f"[DEBUG] Config-Datei {self.config_file} wurde nicht gefunden.")
            return {}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[DEBUG] Geladene config.json: {data}")
        except Exception as e:
            print(f"[DEBUG] Fehler beim Laden der config.json: {e}")
            return {}
        hooks_dict = {}
        for hook in data.get("hooks", []):
            hooks_dict[hook["hookId"]] = hook
        print(f"[DEBUG] Registrierte Hooks: {hooks_dict}")
        return hooks_dict

    def _load_hook_module(self, filename):
        """
        Lädt das Hook-Modul aus dem hooks-Unterordner.
        """
        hook_path = self.hooks_folder / filename
        print(f"[DEBUG] Versuche, Hook-Datei zu laden: {hook_path}")
        if not hook_path.exists():
            raise FileNotFoundError(f"Hook-Datei {filename} wurde in {self.hooks_folder} nicht gefunden.")
        spec = importlib.util.spec_from_file_location("hook_module", hook_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"[DEBUG] Modul {filename} erfolgreich geladen.")
        return module

    def muck(self, hook_id, *args, **kwargs):
        """
        Führt den Hook mit der angegebenen hook_id aus.
        Die Konfiguration wird bei jedem Aufruf neu geladen.
        """
        print("[DEBUG] --- Aufruf von muck() ---")
        self.hooks = self._load_config()  # Neuladen der aktuellen Konfiguration

        print(f"[DEBUG] Versuche, Hook mit ID '{hook_id}' zu finden.")
        hook_config = self.hooks.get(hook_id)
        if not hook_config:
            print(f"[DEBUG] Kein Hook mit der hookId '{hook_id}' gefunden in der aktuellen Konfiguration.")
            return None
        if not hook_config.get("active", False):
            print(f"[DEBUG] Hook '{hook_id}' ist derzeit inaktiv.")
            return None

        try:
            module = self._load_hook_module(hook_config["filename"])
        except FileNotFoundError as e:
            print(f"[DEBUG] {e}")
            return None

        if not hasattr(module, "hook"):
            print(f"[DEBUG] Das Modul '{hook_config['filename']}' enthält keine Funktion 'hook'.")
            return None

        print(f"[DEBUG] Rufe Hook-Funktion mit Argumenten {args} und {kwargs} auf.")
        result = module.hook(*args, **kwargs)
        print(f"[DEBUG] Hook-Funktion zurückgegeben: {result}")
        return result
