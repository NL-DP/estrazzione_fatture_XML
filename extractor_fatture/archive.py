# extractor_fatture/archive.py

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from extractor_fatture.models import TestataFattura
from extractor_fatture.xml_utils import parse_date_iso, sanitize_filename


def build_archive_filename(testata: TestataFattura, source_path: Path) -> str:
    """
    Costruisce il nome file archivio per il file XML già processato.
    Preferisce invoice_id, con fallback a fornitore + numero + data.
    """
    if testata.invoice_id:
        base = sanitize_filename(testata.invoice_id)
    else:
        data_iso = parse_date_iso(testata.data)
        base = "_".join(
            part
            for part in [
                sanitize_filename(testata.fornitore),
                sanitize_filename(testata.numero_fattura),
                sanitize_filename(data_iso),
            ]
            if part
        )

    if not base:
        base = sanitize_filename(source_path.stem) or "fattura"

    return f"{base[:100]}.xml"


def build_archive_path(testata: TestataFattura, source_path: Path, archive_dir: Path) -> Path:
    """
    Restituisce il path finale in archivio.
    Se il file esiste già, aggiunge timestamp per evitare collisioni.
    """
    archive_dir.mkdir(parents=True, exist_ok=True)

    filename = build_archive_filename(testata, source_path)
    destination = archive_dir / filename

    if destination.exists():
        stem = destination.stem[:90]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = archive_dir / f"{stem}_{timestamp}.xml"

    return destination


def move_processed_file(source_path: Path, testata: TestataFattura, archive_dir: Path) -> Path:
    """
    Sposta il file XML processato nella cartella archivio e restituisce il path finale.
    """
    destination = build_archive_path(testata, source_path, archive_dir)
    shutil.move(str(source_path), str(destination))
    return destination
