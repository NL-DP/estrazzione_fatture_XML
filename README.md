# Estrazione Fatture XML

Elabora file XML di fattura elettronica italiana (FPR12/SDI) e produce un file Excel con foglio **Riepilogo** e **Dettaglio**.

---

## Scarica il programma (nessuna installazione richiesta)

Vai alla pagina **[Releases](../../releases)** e scarica il file per il tuo sistema:

| File | Sistema |
|---|---|
| `FattureXML-windows.exe` | Windows 10/11 |
| `FattureXML-linux` | Linux (Ubuntu, Debian, ecc.) |
| `FattureXML-macos` | macOS 12+ |

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

---

## Su macOS

La prima volta fai **tasto destro → Apri → Apri** per bypassare Gatekeeper.

---

## Esecuzione da sorgente (sviluppatori)

```bash
pip install -r requirements.txt
python main.py
```
