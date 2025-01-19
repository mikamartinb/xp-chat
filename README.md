# xp-chat

This is a project for the AI-Project seminar

---

## Anleitung für die Arbeit mit dem Repository

### 1. Bestehende Conda-Umgebung deaktivieren

Bevor du eine neue virtuelle Umgebung mit `venv` erstellst, deaktiviere zuerst deine bestehende `conda`-Umgebung:

```bash
conda deactivate
```

### 2. Repository klonen

Um das Repository zu klonen, führe folgenden Befehl in deinem Terminal aus:

```bash
git clone https://github.com/mikamartinb/xp-chat.git
cd xp-chat
```

### 3. Erstellen einer virtuellen Umgebung (venv)

Um eine saubere und isolierte Python-Umgebung zu haben, verwende eine virtuelle Umgebung. Hier ist, wie du sie einrichtest:

1. Erstelle eine virtuelle Umgebung im Repository-Ordner:

   ```bash
   python3.10 -m venv venv
   ```

2. Aktiviere die virtuelle Umgebung:

   - **Linux/macOS**:

     ```bash
     source venv/bin/activate
     ```

   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

3. Installiere die benötigten Abhängigkeiten (falls vorhanden):
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 4. `.gitignore` anpassen

Es ist wichtig, die virtuelle Umgebung nicht in das Git-Repository hochzuladen. Füge deshalb die folgenden Zeilen zu deiner `.gitignore`-Datei hinzu:

```
# Ignore virtual environment
venv/
```

### 5. Arbeiten mit Branches

Für jede Aufgabe oder jedes Feature, an dem du arbeitest, solltest du einen neuen Branch erstellen. Der Branch-Name sollte das Format `feature<ISSUE-NUMMER>` haben.

#### Beispiel:

Wenn du an Issue #0001 arbeitest, erstelle einen Branch mit folgendem Befehl:

```bash
git checkout -b feature0001
```

#### Schritte zum Arbeiten mit Git:

1. **Neuen Branch erstellen**:  
   Stelle sicher, dass du dich auf dem `main`-Branch befindest, und erstelle dann den neuen Branch:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature<ISSUE-NUMMER>
   ```

2. **Änderungen verfolgen und committen**:  
   Nachdem du Änderungen vorgenommen hast, füge sie zur Staging-Area hinzu:

   ```bash
   git add .
   ```

   Erstelle dann einen Commit mit einer aussagekräftigen Nachricht:

   ```bash
   git commit -m "Beschreibung der Änderungen"
   ```

3. **Änderungen pushen**:  
   Um deinen Branch in das Remote-Repository zu pushen, führe folgenden Befehl aus:

   ```bash
   git push origin feature<ISSUE-NUMMER>
   ```

4. **Pull Request stellen**:  
   Erstelle auf GitHub einen Pull Request, sobald du fertig bist. Stelle sicher, dass du den richtigen Branch und die passende Beschreibung angibst.

### 6. Streamlit App starten

Um die Streamlit App zu starten, gehe wie folgt vor:

1. Stelle sicher, dass deine virtuelle Umgebung aktiv ist.

   - **Linux/macOS**:

     ```bash
     source venv/bin/activate
     ```

   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

2. Starte die Streamlit App im Terminal:

   ```bash
   streamlit run Home.py
   ```

   **Hinweis**: Ersetze `Home.py` durch den entsprechenden Dateinamen, falls deine Startdatei einen anderen Namen hat.

---

Für deploment in .Config File:
[browser]
serverAddress = "aixaiprojekt.leuphana.de"
