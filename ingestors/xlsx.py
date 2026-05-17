import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def _column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return 0
    index = 0
    for char in match.group(1):
        index = index * 26 + ord(char) - 64
    return index - 1


def _shared_strings(zipped: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zipped.namelist():
        return []
    root = ET.fromstring(zipped.read("xl/sharedStrings.xml"))
    return [
        "".join(text.text or "" for text in item.findall(".//main:t", NS))
        for item in root.findall("main:si", NS)
    ]


def _workbook_relationships(zipped: ZipFile) -> dict[str, str]:
    root = ET.fromstring(zipped.read("xl/_rels/workbook.xml.rels"))
    return {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in root.findall("pkgrel:Relationship", NS)
    }


def _sheet_paths(zipped: ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(zipped.read("xl/workbook.xml"))
    relationships = _workbook_relationships(zipped)
    sheets = []
    for sheet in workbook.findall(".//main:sheet", NS):
        relationship_id = sheet.attrib.get(f"{{{NS['rel']}}}id")
        target = relationships.get(relationship_id or "", "")
        path = target if target.startswith("xl/") else f"xl/{target.lstrip('/')}"
        sheets.append((sheet.attrib["name"], path))
    return sheets


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//main:t", NS))

    value = cell.find("main:v", NS)
    if value is None:
        return ""

    raw = value.text or ""
    if cell_type == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type == "b":
        return "TRUE" if raw == "1" else "FALSE"
    return raw


def read_xlsx_tables(
    path: Path, required_field: str | None = None
) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    with ZipFile(path) as zipped:
        shared = _shared_strings(zipped)
        for sheet_name, sheet_path in _sheet_paths(zipped):
            root = ET.fromstring(zipped.read(sheet_path))
            rows = root.findall(".//main:sheetData/main:row", NS)
            if not rows:
                tables[sheet_name] = []
                continue

            headers = _read_row(rows[0], shared)
            sheet_rows = []
            for row in rows[1:]:
                values = _read_row(row, shared)
                if _is_definition_row(values):
                    break
                row_data = {
                    header: values[index] if index < len(values) else ""
                    for index, header in enumerate(headers)
                    if header
                }
                if required_field and not row_data.get(required_field):
                    continue
                if not any(row_data.values()):
                    continue
                sheet_rows.append(row_data)
            tables[sheet_name] = sheet_rows
    return tables


def _read_row(row: ET.Element, shared: list[str]) -> list[str]:
    values_by_index: dict[int, str] = {}
    for cell in row.findall("main:c", NS):
        values_by_index[_column_index(cell.attrib.get("r", ""))] = clean_text(
            _cell_value(cell, shared)
        )
    return [
        values_by_index.get(index, "")
        for index in range(max(values_by_index.keys(), default=-1) + 1)
    ]


def _is_definition_row(values: list[str]) -> bool:
    return len(values) >= 2 and values[0] == "Variable" and values[1] == "Definition"


def clean_text(value: object) -> str:
    text = str(value or "").replace("\xa0", " ").strip()
    if any(marker in text for marker in ("Ã", "Â", "â")):
        try:
            repaired = text.encode("latin1").decode("utf-8")
        except UnicodeError:
            return text
        return repaired
    return text
