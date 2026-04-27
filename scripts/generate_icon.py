#!/usr/bin/env python3
"""
Genera assets/icon.ico — icona 32x32 per il binario Windows.

Usa solo librerie standard (struct). Nessuna dipendenza esterna.
Se Pillow e' disponibile genera un'icona multi-risoluzione (16/32/48/256).
Altrimenti genera un BMP 32x32 embedded in ICO.

Esegui una volta sola:
    python scripts/generate_icon.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Colori (BGRA per BMP)
BG_COLOR   = (100, 56, 31, 255)   # #1F3864 blu scuro (BGRA)
FG_COLOR   = (255, 255, 255, 255) # bianco
EDGE_COLOR = (238, 215, 189, 255) # #BDD7EE bordo chiaro

# Matrice 32x32 della lettera "F" stilizzata (1=testo, 2=bordo, 0=sfondo)
# fmt: off
GLYPH_32 = [
    "00000000000000000000000000000000",
    "00000000000000000000000000000000",
    "00222222222222222222222222222200",
    "02111111111111111111111111111120",
    "02111111111111111111111111111120",
    "02111111111111111111111111111120",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111111111111111111111100000020",
    "02111111111111111111111100000020",
    "02111111111111111111111100000020",
    "02111111111111111111111100000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "02111100000000000000000000000020",
    "00222200000000000000000000000020",
    "00000000000000000000000000222200",
    "00000000000000000000000000000000",
]
# fmt: on

COLOR_MAP = {
    "0": BG_COLOR,
    "1": FG_COLOR,
    "2": EDGE_COLOR,
}


def make_bmp_data(size: int = 32) -> bytes:
    """Crea i dati BMP (senza file header) per una icona size x size."""
    # BMP è bottom-up, quindi invertiamo le righe
    rows = list(reversed(GLYPH_32))

    # Se size != 32, scale nearest-neighbor
    if size != 32:
        scaled_rows = []
        for y in range(size):
            src_y = y * 32 // size
            row = ""
            for x in range(size):
                src_x = x * 32 // size
                row += rows[src_y][src_x]
            scaled_rows.append(row)
        rows = scaled_rows

    # BITMAPINFOHEADER (40 bytes)
    # height è size*2 perché include la AND mask
    bih = struct.pack(
        "<IiiHHIIiiII",
        40,          # biSize
        size,        # biWidth
        size * 2,    # biHeight (XOR + AND)
        1,           # biPlanes
        32,          # biBitCount (BGRA)
        0,           # biCompression
        0,           # biSizeImage
        0,           # biXPelsPerMeter
        0,           # biYPelsPerMeter
        0,           # biClrUsed
        0,           # biClrImportant
    )

    # Pixel data (BGRA, bottom-up)
    pixels = bytearray()
    for row in rows:
        for ch in row:
            b, g, r, a = COLOR_MAP.get(ch, BG_COLOR)
            pixels.extend(struct.pack("BBBB", b, g, r, a))

    # AND mask (1bpp, tutte opache = tutti 0)
    # Ogni riga è allineata a 4 byte
    and_row_bytes = ((size + 31) // 32) * 4
    and_mask = b"\x00" * (and_row_bytes * size)

    return bih + bytes(pixels) + and_mask


def make_ico(sizes: list[int] | None = None) -> bytes:
    """Genera un file ICO completo con le dimensioni specificate."""
    if sizes is None:
        sizes = [32]

    entries_data: list[tuple[int, bytes]] = []
    for s in sizes:
        bmp = make_bmp_data(s)
        entries_data.append((s, bmp))

    # ICO header: 3 x WORD
    num_images = len(entries_data)
    header = struct.pack("<HHH", 0, 1, num_images)

    # Calcola offset dati (dopo header + directory)
    dir_size = 16 * num_images
    data_offset = 6 + dir_size

    directory = bytearray()
    image_data = bytearray()

    for size, bmp in entries_data:
        w = 0 if size >= 256 else size
        h = 0 if size >= 256 else size
        data_size = len(bmp)

        # ICONDIRENTRY: 16 bytes
        entry = struct.pack(
            "<BBBBHHII",
            w,              # bWidth
            h,              # bHeight
            0,              # bColorCount
            0,              # bReserved
            1,              # wPlanes
            32,             # wBitCount
            data_size,      # dwBytesInRes
            data_offset + len(image_data),  # dwImageOffset
        )
        directory.extend(entry)
        image_data.extend(bmp)

    return header + bytes(directory) + bytes(image_data)


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ico_path = ASSETS_DIR / "icon.ico"

    ico_data = make_ico([16, 32, 48])
    ico_path.write_bytes(ico_data)

    print(f"Icona generata: {ico_path} ({len(ico_data)} bytes)")
    print(f"Risoluzioni: 16x16, 32x32, 48x48")


if __name__ == "__main__":
    main()
