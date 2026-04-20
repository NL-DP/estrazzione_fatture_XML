# extractor_fatture/console.py

from __future__ import annotations

from pathlib import Path


def print_banner(input_dir: Path, archive_dir: Path, output_path: Path) -> None:
    """
    Banner iniziale di esecuzione.
    """
    print()
    print("=" * 62)
    print(" EXTRACTOR FATTURE ELETTRONICHE (FPR12 / SDI)")
    print("=" * 62)
    print(f" Input    : {input_dir.resolve()}")
    print(f" Archivio : {archive_dir.resolve()}")
    print(f" Output   : {output_path.resolve()}")

    mode = "APPEND (aggiunge a file esistente)" if output_path.exists() else "NUOVO FILE"
    print(f" Modalita : {mode}")
    print("=" * 62)
    print()


def print_file_status(filename: str, status: str, detail: str = "") -> None:
    """
    Riga di avanzamento per singolo file.
    """
    icon = "[OK] " if status == "OK" else "[SKIP] " if status == "SKIP" else "[ERRORE] "

    if detail:
        print(f" {icon} {filename} -- {detail}")
    else:
        print(f" {icon} {filename}")


def print_summary(
    ok_count: int,
    skip_count: int,
    error_count: int,
    total_rows: int,
    output_path: Path,
) -> None:
    """
    Riepilogo finale elaborazione.
    """
    print()
    print("=" * 62)
    print(" RIEPILOGO ELABORAZIONE")
    print("-" * 62)
    print(f" Nuove fatture importate       : {ok_count}")
    print(f" Fatture gia' presenti (skip) : {skip_count}")
    print(f" File con errori              : {error_count}")
    print(f" Righe totali nel Riepilogo   : {total_rows}")
    print("-" * 62)

    if error_count == 0:
        print(" Completato senza errori.")
    else:
        print(f" {error_count} file non elaborati (rimasti in da_analizzare/).")
        print(" Controlla 'Note Errore' nell'output per i dettagli.")

    print("-" * 62)
    print(f" Output: {output_path.resolve()}")
    print("=" * 62)
    print()
