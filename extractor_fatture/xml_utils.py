from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional


def strip_namespaces(tree: ET.ElementTree) -> ET.ElementTree:
    """
    Rimuove i namespace da tutti i tag XML.
    """
    for el in tree.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
        el.attrib = {
            k.split("}", 1)[1] if "}" in k else k: v
            for k, v in el.attrib.items()
        }
    return tree


def txt(element: Optional[ET.Element], path: str) -> str:
    """
    Legge il testo di un nodo XML in modo sicuro.
    """
    if element is None:
        return ""
    node = element.find(path)
    return node.text.strip() if node is not None and node.text else ""


def to_float(element: Optional[ET.Element], path: str) -> Optional[float]:
    """
    Legge un numero dall'XML gestendo virgola e punto decimale.
    """
    raw = txt(element, path)
    if not raw:
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def nome_anagrafico(dati_anagrafici: Optional[ET.Element]) -> str:
    """
    Estrae Denominazione oppure Nome + Cognome.
    """
    nome = txt(dati_anagrafici, "Anagrafica/Denominazione")
    if not nome:
        n = txt(dati_anagrafici, "Anagrafica/Nome")
        c = txt(dati_anagrafici, "Anagrafica/Cognome")
        nome = f"{n} {c}".strip()
    return nome


def codice_fiscale_iva(dati_anagrafici: Optional[ET.Element]) -> str:
    """
    Restituisce P.IVA se presente, altrimenti Codice Fiscale.
    """
    piva = txt(dati_anagrafici, "IdFiscaleIVA/IdCodice")
    return piva if piva else txt(dati_anagrafici, "CodiceFiscale")


def parse_date_iso(raw: str) -> str:
    """
    Normalizza una data nel formato ISO YYYY-MM-DD.
    Se non riconosciuta, restituisce il valore originale.
    """
    if not raw:
        return ""
    raw = raw.strip()

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return raw


def format_date_display(raw: str) -> str:
    """
    Converte YYYY-MM-DD in DD/MM/YYYY.
    Se non riconosciuta, restituisce il valore originale.
    """
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return raw or ""
