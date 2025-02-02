# XP-Chat

🌍 **Sprache / Language**:  
🇩🇪 [Deutsch](#deutsche-version) | 🇬🇧 [English](#english-version)

---

## 📖 Deutsche Version <a id="deutsche-version"></a>


### I. Benutzeranleitung
#### 1. Repository klonen
```bash
  git clone https://github.com/mikamartinb/xp-chat.git
  cd xp-chat
```
#### 2. Virtuelle Umgebung erstellen und aktivieren
```bash
  python -m venv venv
```
- Aktivieren (Windows)
```bash
  venv\Scripts\activate
```
-  Aktivieren (Mac/Linux)
```bash
  source venv/bin/activate
```

#### 3. Abhängigkeiten installieren
```bash
  pip install -r requirements.txt
```

#### 4. API-Schlüssel hinzufügen (LLM)
- Erstelle ein Datei *`key.secret`* und füge folgenden Schlüssel ein
```bash
  [GDWG]
  API_KEY = "DEIN_SCHLÜSSEL"
```

#### 5. App starten
```bash
  streamlit run app.py
```

---

## 📖 English Version <a id="english-version"></a>


### I. Installation
#### 1. Clone repository
```bash
  git clone https://github.com/mikamartinb/xp-chat.git
  cd xp-chat
```
#### 2. Create and activate a virtual environment
```bash
  python -m venv venv
```
- Activate (Windows)
```bash
  venv\Scripts\activate
```
-  Activate (Mac/Linux)
```bash
  source venv/bin/activate
```

#### 3. Install dependencies
```bash
  pip install -r requirements.txt
```

#### 4. Add API-key (LLM)
- Create a file *`key.secret`* and add a LLM API-key
```bash
  [GDWG]
  API_KEY = "YOUR_KEY"
```

#### 5. Start app
```bash
  streamlit run app.py
```
