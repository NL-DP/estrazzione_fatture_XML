# extractor_fatture/parser.py

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from extractor_fatture.config import MODALITA_PAGAMENTO, TIPO_DOCUMENTO
from extractor_fatture.models import (
    RigaDettaglio,
    RisultatoFattura,
    TestataFattura,
    build_empty_result,
    build_invoice_id,
)
from extractor_fatture.xml_utils import (
    codice_fiscale_iva,
    format_date_display,
    nome_anagrafico,
    parse_date_iso,
    strip_namespaces,
    to_float,
    txt,
)


def is_service_line(desc: str, has_code: bool) -> bool:
    """
    Determina se una riga DettaglioLinee è una riga di servizio da escludere.
    """
    if has_code:
        return False
    if desc.startswith("*"):
        return True
    if desc.lower().startswith("destinaz"):
        return True
    if len(desc) > 120:
        return True
    return False


def parse_lines(body: ET.Element, invoice_id: str) -> list[RigaDettaglio]:
    """
    Estrae le righe articolo dal body della fattura.
    """
    lines: list[RigaDettaglio] = []

    for line_el in body.findall("DatiBeniServizi/DettaglioLinee"):
        descrizione = txt(line_el, "Descrizione")
        codice_el = line_el.find("CodiceArticolo")
        has_code = codice_el is not None

        if is_service_line(descrizione, has_code):
            continue

        quantita = to_float(line_el, "Quantita") or 0.0
        prezzo_totale = to_float(line_el, "PrezzoTotale") or 0.0
        codice = txt(codice_el, "CodiceValore") if has_code else ""

        lines.append(
            RigaDettaglio(
                invoice_id=invoice_id,
                codice=codice,
                descrizione=descrizione,
                quantita=quantita if quantita != 0.0 else None,
                udm=txt(line_el, "UnitaMisura"),
                prezzo_unitario=to_float(line_el, "PrezzoUnitario"),
                prezzo_totale=prezzo_totale if prezzo_totale != 0.0 else None,
                aliquota_iva=to_float(line_el, "AliquotaIVA"),
            )
        )

    return lines


def parse_body(header: ET.Element, body: ET.Element, filename: str) -> RisultatoFattura:
    """
    Estrae i dati di una singola fattura da Header + Body.
    """
    cedente = header.find("CedentePrestatore")
    dati_ced = cedente.find("DatiAnagrafici") if cedente is not None else None
    fornitore = nome_anagrafico(dati_ced)
    fornitore_piva = codice_fiscale_iva(dati_ced)

    cessionario = header.find("CessionarioCommittente")
    dati_ces = cessionario.find("DatiAnagrafici") if cessionario is not None else None
    cliente = nome_anagrafico(dati_ces)
    cliente_piva = codice_fiscale_iva(dati_ces)

    doc = body.find("DatiGenerali/DatiGeneraliDocumento")
    numero_fattura = txt(doc, "Numero")
    data_iso = parse_date_iso(txt(doc, "Data"))
    data_display = format_date_display(data_iso)

    td_raw = txt(doc, "TipoDocumento")
    tipo_documento = TIPO_DOCUMENTO.get(td_raw, td_raw)
    divisa = txt(doc, "Divisa") or "EUR"
    totale = to_float(doc, "ImportoTotaleDocumento")

    riepiloghi = body.findall("DatiBeniServizi/DatiRiepilogo")
    imponibile = (
        sum(to_float(r, "ImponibileImporto") or 0.0 for r in riepiloghi)
        if riepiloghi
        else None
    )
    iva = (
        sum(to_float(r, "Imposta") or 0.0 for r in riepiloghi)
        if riepiloghi
        else None
    )

    pagamento = body.find("DatiPagamento")
    scadenza_iso = parse_date_iso(
        txt(pagamento, "DettaglioPagamento/DataScadenzaPagamento")
    )
    scadenza_pagamento = format_date_display(scadenza_iso)
    iban = txt(pagamento, "DettaglioPagamento/IBAN")

    mp_raw = txt(pagamento, "DettaglioPagamento/ModalitaPagamento")
    modalita_pagamento = MODALITA_PAGAMENTO.get(mp_raw, mp_raw)

    invoice_id = build_invoice_id(
        fornitore_piva=fornitore_piva,
        numero_fattura=numero_fattura,
        data=data_iso,
    )

    testata = TestataFattura(
        file=filename,
        invoice_id=invoice_id,
        numero_fattura=numero_fattura,
        data=data_display,
        tipo_documento=tipo_documento,
        fornitore=fornitore,
        fornitore_piva=fornitore_piva,
        cliente=cliente,
        cliente_piva=cliente_piva,
        divisa=divisa,
        imponibile=imponibile,
        iva=iva,
        totale=totale,
        scadenza_pagamento=scadenza_pagamento,
        iban=iban,
        modalita_pagamento=modalita_pagamento,
        stato="OK",
        errore="",
    )

    linee = parse_lines(body, invoice_id=invoice_id)

    return RisultatoFattura(testata=testata, linee=linee)


def parse_file(xml_path: Path) -> list[RisultatoFattura]:
    """
    Parsa un file XML SDI.
    Gestisce anche i lotti con più FatturaElettronicaBody.
    """
    tree = ET.parse(str(xml_path))
    strip_namespaces(tree)
    root = tree.getroot()

    if "FatturaElettronica" not in root.tag:
        raise ValueError(f"Non è una fattura FPR12 -- root: '{root.tag}'")

    header = root.find("FatturaElettronicaHeader")
    if header is None:
        raise ValueError("FatturaElettronicaHeader mancante")

    bodies = root.findall("FatturaElettronicaBody")
    if not bodies:
        raise ValueError("Nessun FatturaElettronicaBody trovato")

    results: list[RisultatoFattura] = []

    for idx, body in enumerate(bodies, start=1):
        label = (
            xml_path.name
            if len(bodies) == 1
            else f"{xml_path.name} [fattura {idx}/{len(bodies)}]"
        )
        results.append(parse_body(header, body, label))

    return results


def parse_file_safe(xml_path: Path) -> list[RisultatoFattura]:
    """
    Wrapper sicuro: in caso di errore restituisce un risultato ERRORE.
    """
    try:
        return parse_file(xml_path)
    except Exception as exc:
        return [build_empty_result(xml_path.name, str(exc))]
