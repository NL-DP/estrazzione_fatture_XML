# extractor_fatture/config.py

from __future__ import annotations

CARTELLE = {
    "input": "da_analizzare",
    "analizzati": "analizzati",
    "output_excel": "fatture_output.xlsx",
    "output_riepilogo_csv": "fatture_riepilogo.csv",
    "output_dettaglio_csv": "fatture_dettaglio.csv",
    "output_errori_csv": "fatture_errori.csv",
}

SHEET_RIEPILOGO = "Riepilogo"
SHEET_DETTAGLIO = "Dettaglio"

FIELD_MAP_RIEPILOGO = [
    {"key": "file", "label": "File", "width": 28, "format": "text"},
    {"key": "invoice_id", "label": "ID", "width": 32, "format": "text"},
    {"key": "numero_fattura", "label": "N. Fattura", "width": 14, "format": "center"},
    {"key": "data", "label": "Data", "width": 12, "format": "date"},
    {"key": "tipo_documento", "label": "Tipo Doc", "width": 14, "format": "center"},
    {"key": "fornitore", "label": "Fornitore", "width": 30, "format": "text"},
    {"key": "fornitore_piva", "label": "P.IVA Forn.", "width": 16, "format": "center"},
    {"key": "cliente", "label": "Cliente", "width": 30, "format": "text"},
    {"key": "cliente_piva", "label": "P.IVA Cliente", "width": 16, "format": "center"},
    {"key": "divisa", "label": "Divisa", "width": 8, "format": "center"},
    {"key": "imponibile", "label": "Imponibile", "width": 14, "format": "currency", "sumtotal": True},
    {"key": "iva", "label": "IVA", "width": 12, "format": "currency", "sumtotal": True},
    {"key": "totale", "label": "Totale", "width": 14, "format": "currency", "sumtotal": True},
    {"key": "scadenza_pagamento", "label": "Scadenza Pag.", "width": 13, "format": "date"},
    {"key": "iban", "label": "IBAN", "width": 30, "format": "text"},
    {"key": "modalita_pagamento", "label": "Mod. Pag.", "width": 14, "format": "center"},
    {"key": "stato", "label": "Stato", "width": 10, "format": "center"},
    {"key": "errore", "label": "Note Errore", "width": 45, "format": "text"},
]

FIELD_MAP_DETTAGLIO = [
    {"key": "invoice_id", "label": "ID", "width": 32, "format": "text"},
    {"key": "codice", "label": "Codice", "width": 10, "format": "center"},
    {"key": "descrizione", "label": "Descrizione", "width": 42, "format": "text"},
    {"key": "quantita", "label": "Quantita", "width": 10, "format": "number"},
    {"key": "udm", "label": "UdM", "width": 6, "format": "center"},
    {"key": "prezzo_unitario", "label": "P. Unitario", "width": 13, "format": "currency"},
    {"key": "prezzo_totale", "label": "Totale Riga", "width": 13, "format": "currency"},
    {"key": "aliquota_iva", "label": "IVA %", "width": 8, "format": "percent"},
]

COLORI = {
    "header_bg": "1F3864",
    "header_fg": "FFFFFF",
    "riga_ok_a": "E2EFDA",
    "riga_ok_b": "D9EAD3",
    "riga_err": "FCE4D6",
    "totale_bg": "BDD7EE",
    "testo_err": "C0392B",
    "sep_bg": "1F3864",
    "sep_fg": "FFFFFF",
    "det_hdr_bg": "344E6E",
    "det_alt_a": "F5F8FF",
    "det_alt_b": "FFFFFF",
    "det_sub_bg": "D6E4F0",
}

MODALITA_PAGAMENTO = {
    "MP01": "Contanti",
    "MP02": "Assegno",
    "MP03": "Assegno circolare",
    "MP04": "Contanti Tesoreria",
    "MP05": "Bonifico",
    "MP06": "Vaglia cambiario",
    "MP07": "Bollettino banc.",
    "MP08": "Carta di pagamento",
    "MP09": "RID",
    "MP10": "RID utenze",
    "MP11": "RID veloce",
    "MP12": "RIBA",
    "MP13": "MAV",
    "MP14": "Quietanza erario",
    "MP15": "Giroconto",
    "MP16": "Domiciliazione banc.",
    "MP17": "Domiciliazione post.",
    "MP18": "Bollettino c/c post.",
    "MP19": "SEPA Direct Debit",
    "MP20": "SEPA DD core",
    "MP21": "SEPA DD B2B",
    "MP22": "Trattenuta somme",
    "MP23": "PagoPA",
}

TIPO_DOCUMENTO = {
    "TD01": "Fattura",
    "TD02": "Acconto su fattura",
    "TD03": "Acconto su parcella",
    "TD04": "Nota di credito",
    "TD05": "Nota di debito",
    "TD06": "Parcella",
    "TD16": "Int. reverse charge",
    "TD17": "Autofattura serv. esteri",
    "TD18": "Acquisto beni intra",
    "TD19": "Acquisto beni art.17",
    "TD20": "Autofattura denuncia",
    "TD21": "Autofattura splafonamento",
    "TD22": "Estrazione dep. IVA",
    "TD23": "Estrazione dep. IVA+pag.",
    "TD24": "Fattura differita",
    "TD25": "Fattura diff. art.21",
    "TD26": "Cessione beni amm.",
    "TD27": "Fattura autoconsumo",
    "TD28": "Acquisti San Marino",
}

CARTELLE = {
    "input": "da_analizzare",
    "analizzati": "analizzati",
    "errori": "errori",
    "output_excel": "fatture_output.xlsx",
}
