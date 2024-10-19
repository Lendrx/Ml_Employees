# Mitarbeiter-Gruppierungs-Projekt

```
mitarbeiter-gruppierung/
│
├── src/
│   ├── group_employees.py
│   └── generate_sample_data.py
│
├── data/
│   └── .gitkeep
│
├── models/
│   └── .gitkeep
│
├── notebooks/
│   └── .gitkeep
│
├── tests/
│   └── .gitkeep
│
├── requirements.txt
├── README.md
└── .gitignore
```

# Mitarbeiter-Gruppierungs-Projekt

Dieses Projekt enthält Tools zur Gruppierung von Mitarbeitern basierend auf ihren Berufsbezeichnungen und zur Generierung von Beispieldaten für Testzwecke.

## Struktur

- `src/`: Enthält die Hauptskripte
  - `group_employees.py`: Skript zur Gruppierung von Mitarbeitern
  - `generate_sample_data.py`: Skript zur Generierung von Beispieldaten
- `data/`: Verzeichnis für Datendateien
- `models/`: Verzeichnis für gespeicherte Modelle
- `notebooks/`: Jupyter Notebooks für Analysen und Visualisierungen
- `tests/`: Verzeichnis für Testskripte

## Installation

1. Klonen Sie das Repository:
   ```
   git clone https://github.com/ihr-benutzername/mitarbeiter-gruppierung.git
   ```

2. Installieren Sie die erforderlichen Pakete:
   ```
   pip install -r requirements.txt
   ```

## Verwendung

### Generieren von Beispieldaten

Führen Sie das folgende Skript aus, um Beispieldaten zu generieren:

```
python src/generate_sample_data.py
```

### Gruppierung von Mitarbeitern

Führen Sie das folgende Skript aus, um Mitarbeiter zu gruppieren:

```
python src/group_employees.py
```

## Beitragen

Wenn Sie zu diesem Projekt beitragen möchten, erstellen Sie bitte einen Fork des Repositories und reichen Sie einen Pull Request ein.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Details finden Sie in der `LICENSE`-Datei.
```

## .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class

# Verteilungen
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints

# Umgebungen
.env
.venv
env/
venv/
ENV/

# Datendateien
*.csv
*.xlsx

# Modelle
*.joblib

# Systemdateien
.DS_Store
Thumbs.db
```

## requirements.txt

```
pandas==1.3.3
numpy==1.21.2
scikit-learn==0.24.2
joblib==1.0.1
```
