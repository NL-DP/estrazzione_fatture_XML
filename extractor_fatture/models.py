# extractor_fatture/models.py

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional

from extractor_fatture.config import FIELD_MAP_RIEPILOGO


@dataclass
class RigaDettaglio:
    invoice_id: str = ""
    codice: str = ""
    descrizione: str = ""
    quantita: Optional[float] = None
    udm: str = ""
    prezzo_unitario: Optional[float] = None
    prezzo_totale: Optional[float] = None
    aliquota_iva: Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TestataFattura:
    file: str = ""
    invoice_id: str = ""
    numero_fattura: str = ""
    data: str = ""
    tipo_documento: str = ""
    fornitore: str = ""
    fornitore_piva: str = ""
    cliente: str = ""
    cliente_piva: str = ""
    divisa: str = "EUR"
    imponibile: Optional[float] = None
    iva: Optional[float] = None
    totale: Optional[float] = None
    scadenza_pagamento: str = ""
    iban: str = ""
    modalita_pagamento: str = ""
    stato: str = "OK"
    errore: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RisultatoFattura:
    testata: TestataFattura
    linee: list[RigaDettaglio] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "testata": self.testata.to_dict(),
            "linee": [linea.to_dict() for linea in self.linee],
        }


def build_invoice_id(fornitore_piva: str, numero_fattura: str, data: str) -> str:
    """
    ID logico fattura:
    PIVA_FORNITORE|NUMERO_FATTURA|DATA_ISO
    """
    parts = [
        (fornitore_piva or "").strip().upper(),
        (numero_fattura or "").strip().upper(),
        (data or "").strip(),
    ]
    return "|".join(parts)


def build_empty_result(filename: str, errore: str) -> RisultatoFattura:
    """
    Crea un risultato vuoto compatibile con il foglio Riepilogo.
    """
    valid_keys = {field["key"] for field in FIELD_MAP_RIEPILOGO}

    values = {key: None for key in valid_keys}
    values.update(
        {
            "file": filename,
            "invoice_id": "",
            "divisa": "EUR",
            "stato": "ERRORE",
            "errore": errore,
        }
    )

    testata = TestataFattura(
        file=values.get("file") or "",
        invoice_id=values.get("invoice_id") or "",
        numero_fattura=values.get("numero_fattura") or "",
        data=values.get("data") or "",
        tipo_documento=values.get("tipo_documento") or "",
        fornitore=values.get("fornitore") or "",
        fornitore_piva=values.get("fornitore_piva") or "",
        cliente=values.get("cliente") or "",
        cliente_piva=values.get("cliente_piva") or "",
        divisa=values.get("divisa") or "EUR",
        imponibile=values.get("imponibile"),
        iva=values.get("iva"),
        totale=values.get("totale"),
        scadenza_pagamento=values.get("scadenza_pagamento") or "",
        iban=values.get("iban") or "",
        modalita_pagamento=values.get("modalita_pagamento") or "",
        stato=values.get("stato") or "ERRORE",
        errore=values.get("errore") or errore,
    )

    return RisultatoFattura(testata=testata, linee=[])
