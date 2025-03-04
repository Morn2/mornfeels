#!/bin/bash

# Führe git add . aus, um alle Änderungen hinzuzufügen
git add .

# Lese die Commit-Nachricht als Parameter oder verwende eine Standardnachricht
commit_message=${1:-"Automatisches Update"}

# Führe git commit aus
git commit -m "$commit_message"

# Führe git push aus
git push origin main
