# Estrazione Fatture XML

Elabora file XML di fattura elettronica italiana (FPR12/SDI) e produce un file Excel con foglio **Riepilogo** e **Dettaglio**.

---

## Scarica il programma (nessuna installazione richiesta)

Vai alla pagina **[Releases](../../releases)** e scarica il file per il tuo sistema:

| File | Sistema |
|---|---|
| `FattureXML-windows.exe` | Windows 10/11 |
| `FattureXML-linux` | Linux (Ubuntu, Debian, ecc.) |
| `FattureXML-macos` | macOS 12+ (Intel e Apple Silicon via Rosetta) |

---

## Come usarlo

Crea una cartella di lavoro con questa struttura:

```
FattureXML/
├── FattureXML-windows.exe   ← l'eseguibile scaricato
├── da_analizzare/           ← metti qui i file XML
├── analizzati/              (creata automaticamente)
└── errori/                  (creata automaticamente)
```

Fai doppio clic sull'eseguibile oppure lancialo da terminale. Produce `fatture_output.xlsx` nella stessa cartella.

### Opzioni da riga di comando

```
FattureXML-windows.exe --input CARTELLA_XML --output PERCORSO.xlsx
FattureXML-windows.exe --version
FattureXML-windows.exe --help
```

---

## Note per piattaforma

### Windows

Il binario è compilato con Nuitka (GCC/MinGW) e non è firmato con certificato digitale. Alcuni antivirus potrebbero mostrare un avviso al primo avvio — è un falso positivo comune per tutti gli eseguibili Python compilati non firmati. Il programma non accede alla rete, non modifica file di sistema e opera solo nelle cartelle indicate.

Se Windows Defender blocca il file: **Altre informazioni → Esegui comunque**.

### macOS

La prima volta fai **tasto destro → Apri → Apri** per bypassare Gatekeeper.

Su Apple Silicon (M1/M2/M3) il binario gira tramite Rosetta 2 (già incluso nel sistema).

### Linux

```bash
chmod +x FattureXML-linux
./FattureXML-linux
```

---

## Esecuzione da sorgente (sviluppatori)

```bash
pip install -r requirements.txt
python main.py
```

---

## Build locale (senza CI)

### Prerequisiti

- Python 3.11
- Su Linux: `sudo apt install patchelf ccache`

### Comandi

```bash
pip install -r requirements.txt
pip install "nuitka>=2.1" ordered-set zstandard

# Genera icona (una volta sola)
python scripts/generate_icon.py

# Windows
python -m nuitka --onefile --standalone --follow-imports --mingw64 \
  --onefile-no-compression \
  --include-package=extractor_fatture --include-package=openpyxl \
  --include-package=et_xmlfile --include-package-data=openpyxl \
  --nofollow-import-to=tkinter --nofollow-import-to=matplotlib \
  --nofollow-import-to=numpy --nofollow-import-to=pandas \
  --nofollow-import-to=setuptools --nofollow-import-to=pip \
  --windows-console-mode=attach --windows-uac-admin=no \
  --company-name=FattureXML --product-name=FattureXML \
  --file-version=1.0.0.0 --product-version=1.0.0.0 \
  --file-description="Estrazione fatture elettroniche XML" \
  --windows-icon-from-ico=assets/icon.ico \
  --assume-yes-for-downloads \
  --output-filename=FattureXML-windows.exe --output-dir=dist \
  main.py

# Linux
python -m nuitka --onefile --standalone --follow-imports \
  --include-package=extractor_fatture --include-package=openpyxl \
  --include-package=et_xmlfile --include-package-data=openpyxl \
  --nofollow-import-to=tkinter --nofollow-import-to=matplotlib \
  --nofollow-import-to=numpy --nofollow-import-to=pandas \
  --nofollow-import-to=setuptools --nofollow-import-to=pip \
  --assume-yes-for-downloads \
  --output-filename=FattureXML-linux --output-dir=dist \
  main.py

# macOS
python -m nuitka --onefile --standalone --follow-imports \
  --include-package=extractor_fatture --include-package=openpyxl \
  --include-package=et_xmlfile --include-package-data=openpyxl \
  --nofollow-import-to=tkinter --nofollow-import-to=matplotlib \
  --nofollow-import-to=numpy --nofollow-import-to=pandas \
  --nofollow-import-to=setuptools --nofollow-import-to=pip \
  --assume-yes-for-downloads \
  --output-filename=FattureXML-macos --output-dir=dist \
  main.py
codesign --deep --force --options runtime --sign '-' dist/FattureXML-macos
```

---

## Release

Per creare una nuova release:

```bash
# Aggiorna la versione in extractor_fatture/version.py
# Poi:
git add -A && git commit -m "release v1.1.0"
git tag v1.1.0
git push && git push --tags
```

Il workflow GitHub Actions compila automaticamente per tutte le piattaforme e pubblica i binari nella release.
