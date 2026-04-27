from __future__ import annotations

import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from extractor_fatture.config import CARTELLE
from extractor_fatture.dedupe import is_already_processed, read_processed_invoice_ids
from extractor_fatture.export_excel import build_excel
from extractor_fatture.models import RisultatoFattura
from extractor_fatture.parser import parse_file_safe
from extractor_fatture.storage import (
    archive_xml_name,
    ensure_directories,
    error_xml_name,
    glob_xml_files,
)
from extractor_fatture.version import __version__

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)

log = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """
    Restituisce la cartella base dove cercare da_analizzare/, analizzati/, ecc.

    Compatibile con:
      - Nuitka --onefile  -> sys.argv[0] punta al binario originale
      - Nuitka standalone -> sys.argv[0] punta al binario nella .dist
      - PyInstaller       -> sys.frozen == True, sys.executable e' il binario
      - Esecuzione da sorgente Python -> sys.argv[0] e' main.py
    """
    # PyInstaller: sys.executable punta al binario, non all'interprete
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    # Nuitka e sorgente Python: sys.argv[0] punta sempre al file/binario
    # che e' stato lanciato, anche in Nuitka onefile (NON la temp dir)
    return Path(sys.argv[0]).resolve().parent


def print_banner(input_dir: Path, analizzati_dir: Path, errori_dir: Path, output_path: Path) -> None:
    print()
    print("=" * 62)
    print(f" EXTRACTOR FATTURE ELETTRONICHE v{__version__} (FPR12 / SDI)")
    print("=" * 62)
    print(f" Input    : {input_dir.resolve()}")
    print(f" Archivio : {analizzati_dir.resolve()}")
    print(f" Errori   : {errori_dir.resolve()}")
    print(f" Output   : {output_path.resolve()}")
    mode = "APPEND (aggiunge a file esistente)" if output_path.exists() else "NUOVO FILE"
    print(f" Modalita : {mode}")
    print("=" * 62)
    print()


def print_file_row(nome: str, stato: str, dettaglio: str = "") -> None:
    icon = "[OK] " if stato == "OK" else "[SKIP] " if stato == "SKIP" else "[ERRORE] "
    if dettaglio:
        print(f" {icon} {nome} -- {dettaglio}")
    else:
        print(f" {icon} {nome}")


def print_summary(ok: int, skip: int, errori: int, righe: int, output_path: Path) -> None:
    print()
    print("=" * 62)
    print(" RIEPILOGO ELABORAZIONE")
    print("-" * 62)
    print(f" Nuove fatture importate     : {ok}")
    print(f" Fatture gia' presenti (skip): {skip}")
    print(f" File con errori             : {errori}")
    print(f" Righe totali nel Riepilogo  : {righe}")
    print("-" * 62)
    if errori == 0:
        print(" Completato senza errori.")
    else:
        print(f" {errori} file spostati nella cartella errori.")
    print("-" * 62)
    print(f" Output: {output_path.resolve()}")
    print("=" * 62)
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estrazione fatture XML verso Excel")
    parser.add_argument("--version", action="version", version=f"FattureXML {__version__}")
    parser.add_argument("--input", default=None, help="Cartella XML input")
    parser.add_argument("--analizzati", default=None, help="Cartella archivio XML elaborati")
    parser.add_argument("--errori", default=None, help="Cartella XML con errori")
    parser.add_argument("--output", default=None, help="File Excel output")
    return parser.parse_args()


def _unique_skip_destination(xml_path: Path, analizzati_dir: Path) -> Path:
    dest = analizzati_dir / xml_path.name
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = analizzati_dir / f"{xml_path.stem}_SKIP_{ts}{xml_path.suffix}"
    return dest


def main() -> None:
    args = parse_args()
    base_dir = get_base_dir()

    input_dir = Path(args.input) if args.input else base_dir / CARTELLE["input"]
    analizzati_dir = Path(args.analizzati) if args.analizzati else base_dir / CARTELLE["analizzati"]
    errori_dir = Path(args.errori) if args.errori else base_dir / CARTELLE["errori"]
    output_path = Path(args.output) if args.output else base_dir / CARTELLE["output_excel"]

    ensure_directories(input_dir, analizzati_dir, errori_dir)
    print_banner(input_dir, analizzati_dir, errori_dir, output_path)

    xml_files = glob_xml_files(input_dir)
    processed_ids = read_processed_invoice_ids(output_path)

    risultati_da_scrivere: list[RisultatoFattura] = []
    ok_count = 0
    skip_count = 0
    err_count = 0

    for xml_path in xml_files:
        log.info("Processo file: %s", xml_path.name)

        try:
            parsed_results = parse_file_safe(xml_path)

            risultati_nuovi: list[RisultatoFattura] = []
            file_has_error_rows = False
            file_skip_count = 0

            for result in parsed_results:
                if result.testata.stato != "OK":
                    risultati_da_scrivere.append(result)
                    file_has_error_rows = True
                    continue

                invoice_id = (result.testata.invoice_id or "").strip()

                if is_already_processed(invoice_id, processed_ids):
                    skip_count += 1
                    file_skip_count += 1
                    log.info(" SKIP invoice_id=%s", invoice_id)
                    continue

                risultati_nuovi.append(result)
                processed_ids.add(invoice_id)

            if risultati_nuovi:
                risultati_da_scrivere.extend(risultati_nuovi)

                dest = archive_xml_name(risultati_nuovi[0].testata, xml_path, analizzati_dir)
                shutil.move(str(xml_path), str(dest))

                articoli = sum(len(r.linee) for r in risultati_nuovi)
                ok_count += len(risultati_nuovi)

                dettaglio = f"{len(risultati_nuovi)} fatture, {articoli} articoli"
                if file_skip_count:
                    dettaglio += f", {file_skip_count} duplicate"
                if file_has_error_rows:
                    dettaglio += ", con alcune righe fattura in errore"

                print_file_row(xml_path.name, "OK", dettaglio)
                log.info(" OK -> %s", dest.name)

            elif file_has_error_rows:
                dest_err = error_xml_name(xml_path, errori_dir)
                shutil.move(str(xml_path), str(dest_err))
                err_count += 1
                print_file_row(xml_path.name, "ERRORE", f"spostato in {dest_err.name}")
                log.error(" ERRORE -> %s", dest_err.name)

            else:
                dest_skip = _unique_skip_destination(xml_path, analizzati_dir)
                shutil.move(str(xml_path), str(dest_skip))
                print_file_row(xml_path.name, "SKIP", f"gia' presente, spostato in {dest_skip.name}")
                log.info(" SKIP -> %s", dest_skip.name)

        except Exception as exc:
            msg = str(exc)
            log.error("Errore su %s: %s", xml_path.name, msg)

            try:
                dest_err = error_xml_name(xml_path, errori_dir)
                shutil.move(str(xml_path), str(dest_err))
                print_file_row(xml_path.name, "ERRORE", f"{msg} -> spostato in {dest_err.name}")
            except Exception as move_exc:
                log.error("Impossibile spostare %s in errori: %s", xml_path.name, move_exc)
                print_file_row(xml_path.name, "ERRORE", msg)

            err_count += 1

    if risultati_da_scrivere:
        build_excel(risultati_da_scrivere, output_path)

    righe_riepilogo = len(risultati_da_scrivere)
    print_summary(ok_count, skip_count, err_count, righe_riepilogo, output_path)

    n_articoli = sum(len(r.linee) for r in risultati_da_scrivere if r.testata.stato == "OK")
    log.info(
        "Completato -- OK: %d SKIP: %d ERR: %d Articoli: %d",
        ok_count,
        skip_count,
        err_count,
        n_articoli,
    )


if __name__ == "__main__":
    main()
