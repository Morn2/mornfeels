#!/bin/bash

# Führe git add . aus, um alle Änderungen hinzuzufügen
git add .

# Lese die Commit-Nachricht als Parameter oder verwende eine Standardnachricht
commit_message=${1:-"Non specific commit message"}

# Führe git commit aus
git commit -m "$commit_message"

# Aktuellen Branch ermitteln
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Führe git push aus
git push origin "$current_branch"
