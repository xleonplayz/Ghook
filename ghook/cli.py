import argparse
import json
import uuid
import shutil
from pathlib import Path
from ghook.hook_manager import DEFAULT_PROJECT_DIR

def init_command():
    """
    Initialisiert das globale G-Hook-Projektverzeichnis (standardmäßig ~/.ghook_project).
    Falls das Verzeichnis bereits existiert, wird der Nutzer gefragt, ob es gelöscht und neu erstellt werden soll.
    """
    project_dir = DEFAULT_PROJECT_DIR
    
    if project_dir.exists():
        answer = input(f"Das Projektverzeichnis {project_dir} existiert bereits. Möchtest du es löschen und neu erstellen? (y/n): ")
        if answer.strip().lower() == "y":
            shutil.rmtree(project_dir)
            print(f"{project_dir} wurde gelöscht.")
        else:
            print("Initialisierung abgebrochen.")
            return

    project_dir.mkdir(parents=True, exist_ok=True)
    print(f"Erstellt globales Projektverzeichnis: {project_dir}")
    
    config_file = project_dir / "config.json"
    config = {"hooks": []}
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print("Erstellt config.json im globalen Projektverzeichnis.")
    
    hooks_folder = project_dir / "hooks"
    hooks_folder.mkdir()
    print(f"Erstellt hooks-Ordner: {hooks_folder}")

def push_command():
    """
    Registriert neue Hooks: Scannt den hooks-Unterordner im globalen Projektverzeichnis
    nach neuen Python-Dateien und fügt sie der config.json hinzu.
    """
    project_dir = DEFAULT_PROJECT_DIR
    config_file = project_dir / "config.json"
    hooks_folder = project_dir / "hooks"

    if not project_dir.exists():
        print(f"Projektverzeichnis {project_dir} existiert nicht. Bitte führe 'ghook init' aus.")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    existing_files = {hook["filename"] for hook in config["hooks"]}

    for file in hooks_folder.iterdir():
        if file.is_file() and file.suffix == ".py" and file.name not in existing_files:
            with open(file, "r", encoding="utf-8") as f:
                first_lines = f.read(200)
            description = "Keine Beschreibung angegeben."
            if first_lines.startswith('"""'):
                end_index = first_lines.find('"""', 3)
                if end_index != -1:
                    description = first_lines[3:end_index].strip()
            hook_id = f"hook_{uuid.uuid4().hex[:6]}"
            new_hook = {
                "hookId": hook_id,
                "filename": file.name,
                "description": description,
                "active": True
            }
            config["hooks"].append(new_hook)
            print(f"Registrierter neuer Hook: {file.name} mit ID {hook_id}")

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print("Aktualisierte config.json im globalen Projektverzeichnis.")

def clear_command():
    """
    Löscht das globale G-Hook-Projektverzeichnis (standardmäßig ~/.ghook_project)
    inklusive aller Konfigurationsdateien und Hooks. Der Nutzer wird zur Bestätigung aufgefordert.
    """
    project_dir = DEFAULT_PROJECT_DIR
    if project_dir.exists():
        answer = input(f"Soll das globale G-Hook-Verzeichnis {project_dir} wirklich gelöscht werden? (y/n): ")
        if answer.strip().lower() == "y":
            shutil.rmtree(project_dir)
            print(f"{project_dir} wurde gelöscht.")
        else:
            print("Clear-Vorgang abgebrochen.")
    else:
        print(f"{project_dir} existiert nicht.")

def main():
    parser = argparse.ArgumentParser(prog="ghook", description="G-Hook CLI")
    subparsers = parser.add_subparsers(dest="command", help="Befehle")

    subparsers.add_parser("init", help="Initialisiert das globale G-Hook-Projektverzeichnis (standardmäßig ~/.ghook_project)")
    subparsers.add_parser("push", help="Registriert neue Hooks und aktualisiert die config.json")
    subparsers.add_parser("clear", help="Löscht das globale G-Hook-Projektverzeichnis inkl. aller Configs und Hooks")

    args = parser.parse_args()
    if args.command == "init":
        init_command()
    elif args.command == "push":
        push_command()
    elif args.command == "clear":
        clear_command()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
