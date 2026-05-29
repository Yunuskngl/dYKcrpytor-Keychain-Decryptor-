# Dynamic table model for decrypted dict rows.

from __future__ import annotations

import binascii
from typing import Any, List

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt


def format_cell(val: Any) -> str:
    if isinstance(val, bytes):
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            return "0x" + binascii.hexlify(val).decode("ascii")
    return str(val)


class DictRecordsModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[dict] = []
        self._columns: List[str] = []

    def set_records(self, records: list) -> None:
        self.beginResetModel()
        self._rows = []
        keys: set[str] = set()
        for r in records:
            if not isinstance(r, dict) or not r:
                continue
            keys.update(str(k) for k in r.keys())
            self._rows.append({str(k): r[k] for k in r.keys()})
        self._columns = sorted(keys)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._columns)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            row = self._rows[index.row()]
            col = self._columns[index.column()]
            return format_cell(row.get(col, ""))
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._columns[section] if 0 <= section < len(self._columns) else ""
        return str(section + 1)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        if not self._rows or column < 0 or column >= len(self._columns):
            return
        col_name = self._columns[column]
        reverse = order == Qt.SortOrder.DescendingOrder

        def sort_key(row: dict) -> str:
            return format_cell(row.get(col_name, "")).casefold()

        self.layoutAboutToBeChanged.emit()
        self._rows.sort(key=sort_key, reverse=reverse)
        self.layoutChanged.emit()
