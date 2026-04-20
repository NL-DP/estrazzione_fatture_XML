from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from extractor_fatture.models import TestataFattura


def ensure_directories(input_dir: Path, analizzati_dir: Path, errori_dir: Path) -> None:
    """
    Crea automaticamente le cartelle di lavoro se non esistono.
    """
    input_dir.mkdir(parents=True, exist_ok=True)
    analizzati_dir.mkdir(parents=True, exist_ok=True)
    errori_dir.mkdir(parents=True, exist_ok=True)


def glob_xml_files(directory: Path) -> list[Path]:
    """
    Trova tutti i file XML nella cartella, case-insensitive.
    """
    files = list(directory.glob("*.xml")) + list(directory.glob("*.XML"))
    seen = set()
    result: list[Path] = []

    for f in files:
        if f.name not in seen:
            seen.add(f.name)
            result.append(f)

    return sorted(result)


def sanitize_filename(value: str) -> str:
    """
    Rimuove i caratteri non validi dai nomi file.
    """
    value = re.sub(r'[\\/:*?"<>|]', "_", value or "")
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_. ")


def archive_xml_name(testata: TestataFattura, xml_path: Path, target_dir: Path) -> Path:
    """
    Costruisce il nome archivio XML:
    {Fornitore}_{NumeroFattura}_{DataISO}.xml
    Se esiste già, aggiunge timestamp.
    """
    fornitore = getattr(testata, "fornitore", "") or ""
    numero_fattura = getattr(testata, "numero_fattura", "") or ""
    data = getattr(testata, "data", "") or ""

    if not fornitore and not numero_fattura:
        base = xml_path.stem
    else:
        data_iso = _to_iso_from_display(data)
        base = "{}_{}_{}".format(
            sanitize_filename(fornitore),
            sanitize_filename(numero_fattura),
            sanitize_filename(data_iso),
        )[:100]

    dest = target_dir / f"{base}.xml"

    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = target_dir / f"{base[:90]}_{ts}.xml"

    return dest


def error_xml_name(xml_path: Path, errori_dir: Path) -> Path:
    """
    Costruisce il nome file per la cartella errori.
    Mantiene il nome originale sanificato; se esiste già, aggiunge timestamp.
    """
    base = sanitize_filename(xml_path.stem)[:100]
    dest = errori_dir / f"{base}.xml"

    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = errori_dir / f"{base[:90]}_{ts}.xml"

    return dest


def _to_iso_from_display(value: str) -> str:
    """
    Converte DD/MM/YYYY in YYYY-MM-DD se possibile.
    """
    try:
        return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return value or ""
