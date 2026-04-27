# Estrazione Fatture XML

Elabora file XML di fattura elettronica italiana (FPR12/SDI) e produce un file Excel con foglio **Riepilogo** e **Dettaglio**.

---

## Scarica

Vai alla pagina **[Releases](../../releases)** e scarica il file per il tuo sistema:

| File | Sistema |
|---|---|
| `FattureXML-windows.zip` | Windows 10/11 |
| `FattureXML-macos.zip` | macOS 12+ (Intel e Apple Silicon) |
| `FattureXML-linux` | Linux (Ubuntu, Debian, ecc.) |

Non serve installare Python né nessun altro programma.

---

## Windows

1. Scarica `FattureXML-windows.zip` dalla pagina Releases
2. Estrai lo zip in una cartella a piacere
3. Metti i file XML in `da_analizzare/`
4. Doppio clic su **FattureXML.bat**
5. Il risultato è in `fatture_output.xlsx`

```
FattureXML/
├── FattureXML.bat          ← doppio clic per avviare
├── da_analizzare/          ← metti qui i file XML
├── analizzati/             ← fatture elaborate (automatica)
├── errori/                 ← file con problemi (automatica)
├── fatture_output.xlsx     ← risultato
└── _runtime/               ← motore del programma, non toccare
```

---

## macOS

1. Scarica `FattureXML-macos.zip` dalla pagina Releases
2. Estrai lo zip
3. Metti i file XML in `da_analizzare/`
4. Doppio clic su **FattureXML.command**

Se macOS dice "non può verificare lo sviluppatore":
**Impostazioni di Sistema → Privacy e Sicurezza → scorri in basso → "Apri comunque"**

Oppure da Terminale:

```bash
chmod +x FattureXML.command
./FattureXML.command
```

---

## Linux

```bash
chmod +x FattureXML-linux
mkdir -p da_analizzare
# copia i file XML in da_analizzare/
./FattureXML-linux
```

---

## Come funziona

Il programma:

1. Legge tutti i file XML dalla cartella `da_analizzare/`
2. Estrae i dati di ogni fattura (fornitore, cliente, importi, articoli, pagamento)
3. Scrive tutto in `fatture_output.xlsx` con due fogli:
   - **Riepilogo** — una riga per fattura con totali, stato, scadenza
   - **Dettaglio** — una riga per articolo, filtrabile
4. Sposta i file elaborati in `analizzati/`, quelli con errori in `errori/`
5. Se il file Excel esiste già, aggiunge le nuove fatture senza duplicati

### Formati supportati

- Fatture elettroniche FPR12 (formato SDI)
- File XML singoli o lotti con più fatture nello stesso file
- Tutti i tipi documento: TD01 (fattura), TD04 (nota di credito), TD24 (differita), ecc.

### Opzioni avanzate (da terminale)

```
FattureXML.bat --input ALTRA_CARTELLA --output ALTRO_FILE.xlsx
FattureXML.bat --version
FattureXML.bat --help
```

---

## Per sviluppatori

### Esecuzione da sorgente

```bash
pip install -r requirements.txt
python main.py
```

### Struttura del codice

```
extractor_fatture/
├── config.py          — configurazione cartelle, campi Excel, codici pagamento
├── parser.py          — parsing XML fattura elettronica
├── xml_utils.py       — utility lettura nodi XML
├── models.py          — dataclass TestataFattura, RigaDettaglio
├── dedupe.py          — deduplica fatture già importate
├── export_excel.py    — generazione file Excel (Riepilogo + Dettaglio)
├── storage.py         — gestione file e cartelle
└── version.py         — versione del programma
```

### Nuova release

```bash
# 1. Aggiorna la versione in extractor_fatture/version.py
# 2. Commit e tag
git add -A && git commit -m "release vX.Y.Z"
git tag vX.Y.Z
git push && git push --tags
```

Il workflow GitHub Actions compila automaticamente per tutte le piattaforme e pubblica i file nella Release.
