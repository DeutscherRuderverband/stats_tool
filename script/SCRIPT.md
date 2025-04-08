# Anwendung des Datenbankskripts

## Wofür ist das Skript?

Dieses Skript ermöglicht es, Wettkampfergebnisse aus der Datenbank, die in Railway gehostet wird, für einen definierten Zeitraum abzufragen. Die abgefragten Ergebnisse werden anschließend in einer Excel-Datei gespeichert.

## Voraussetzungen
Um das Skript auszuführen, musst du sicherstellen, dass Python 3.12 und die benötigten Bibliotheken installiert sind.

#### 1. Variante – Python direkt installieren

**Benötigte Python-Version:**
- Python 3.10

**Benötigte Bibliotheken:**
- `sqlalchemy`
- `pandas`
- `psycopg2`
- `openpyxl`

**Installation der Bibliotheken:**
```bash
pip install sqlalchemy=1.4.54 pandas psycopg2-binary=2.9.10 openpyxl
```

#### 2. Variante – Anaconda

Alternativ kann auch Anaconda verwendet werden:

1. **Anaconda herunterladen und installieren**: [Anaconda](https://www.anaconda.com/products/individual).
2. **Umgebung mit einer `environment.yml` Datei erstellen**:
   - Lade die `environment.yml` Datei herunter.
   - Erstelle die Umgebung mit dem folgenden Befehl:
     ```bash
     conda env create -f environment.yml
     ```

## Anwendung des Datenbankskripts

1. **Ordner herunterladen**:
   - Lade den Ordner `stats_tool/script` von GitHub herunter.
     - **Option a:** Lade die code.zip Datei direkt aus dem GitHub-Repository herunter und extrahiere die Dateien in einen neuen Ordner.
     - **Option b:** Wenn Git installiert ist, klone das gesamte Repository mit Git:
       ```bash
       git clone https://github.com/DeutscherRuderverband/stats_tool.git
       ```

2. **Werte in `variables.py` anpassen**:
   - Öffne die Datei `variables.py` und passe die folgenden Variablen an:
     - `DATE_FROM`: Startdatum der Abfrage (im Format `YYYY-MM-DD`).
     - `DATE_TO`: Enddatum der Abfrage (im Format `YYYY-MM-DD`).
     - `DATABASE_URL`: Die URL der PostgreSQL-Datenbank. Ersetze `username`, `password`, `host`, `port` und `database_name` durch die entsprechenden Werte aus Railway.

3. **Skript ausführen**:
   - Öffne das Terminal und navigiere zum Ordner, der die Code-Dateien, also auch `main.py` enthält.
   - Starte das Skript mit folgendem Befehl:
     ```bash
     python main.py
     ```

---

**Zusätzliche Hinweise:**
- Stelle sicher, dass die Datenbank erreichbar ist und die Zugangsdaten korrekt sind.
