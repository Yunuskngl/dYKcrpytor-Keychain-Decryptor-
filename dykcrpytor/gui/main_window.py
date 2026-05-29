# Main application window.

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from dykcrpytor.app_icon import icon_png_path
from dykcrpytor.gui.models import DictRecordsModel
from dykcrpytor.gui.styles import APP_NAME, APP_STYLESHEET
from dykcrpytor.gui.worker import DecryptWorker
from dykcrpytor.keychain.service import export_keychain_to_sqlite, validate_keychain_file


class DropPathEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(40)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            local = urls[0].toLocalFile()
            if local:
                self.setText(local)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(980, 660)
        self.resize(1120, 740)

        self._data: dict | None = None
        self._worker: DecryptWorker | None = None

        self._model_genp = DictRecordsModel(self)
        self._model_inet = DictRecordsModel(self)

        central = QWidget()
        central.setObjectName("centralRoot")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 22, 24, 16)
        root.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("heroCard")
        hero_l = QVBoxLayout(hero)
        hero_l.setContentsMargins(22, 18, 22, 18)
        hero_l.setSpacing(4)
        ht = QLabel(APP_NAME)
        ht.setObjectName("heroTitle")
        hs = QLabel("iOS keychain çözümleme · tablo görünümü · SQLite (.db) dışa aktarma")
        hs.setObjectName("heroTagline")
        hs.setWordWrap(True)
        hero_l.addWidget(ht)
        hero_l.addWidget(hs)
        root.addWidget(hero)

        panel = QFrame()
        panel.setObjectName("panelCard")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(22, 20, 22, 20)
        pl.setSpacing(14)

        sec = QLabel("Kaynak dosya (.db veya .plist)")
        sec.setObjectName("sectionLabel")
        pl.addWidget(sec)

        path_row = QHBoxLayout()
        path_row.setSpacing(10)
        self._path_edit = DropPathEdit()
        self._path_edit.setPlaceholderText(
            "keychain-2.db veya backup_keychain_v2.plist — sürükleyip bırakabilirsiniz"
        )
        btn_browse = QPushButton("Dosya seç")
        btn_browse.setObjectName("secondaryButton")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_file)
        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(btn_browse)
        pl.addLayout(path_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self._btn_run = QPushButton("Analiz et ve çöz")
        self._btn_run.setObjectName("primaryButton")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.clicked.connect(self._start_decrypt)
        self._btn_export = QPushButton("SQLite olarak dışa aktar")
        self._btn_export.setObjectName("accentOutline")
        self._btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_export.setEnabled(False)
        self._btn_export.clicked.connect(self._export_db)
        btn_row.addWidget(self._btn_run)
        btn_row.addWidget(self._btn_export)
        btn_row.addStretch(1)
        pl.addLayout(btn_row)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        pl.addWidget(self._progress)

        root.addWidget(panel)

        info = QFrame()
        info.setObjectName("infoStrip")
        info_lo = QVBoxLayout(info)
        info_lo.setContentsMargins(0, 0, 0, 0)
        info_txt = QLabel(
            "<b>SQLite (.db):</b> keyclass ≥ 6 için SSH + <code>keyclass_unwrapper</code> gerekir.<br>"
            "<b>backup_keychain_v2.plist:</b> anahtarlar plist içinde açılmıştır; "
            "aynı AES-GCM yöntemi, SSH gerekmez."
        )
        info_txt.setObjectName("infoStripText")
        info_txt.setWordWrap(True)
        info_txt.setTextFormat(Qt.TextFormat.RichText)
        info_lo.addWidget(info_txt)
        root.addWidget(info)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setMovable(False)
        self._tv_genp = QTableView()
        self._tv_inet = QTableView()
        self._tv_genp.setModel(self._model_genp)
        self._tv_inet.setModel(self._model_inet)
        for tv in (self._tv_genp, self._tv_inet):
            tv.horizontalHeader().setStretchLastSection(True)
            tv.verticalHeader().setVisible(False)
            tv.setAlternatingRowColors(True)
            tv.setShowGrid(True)
            tv.setSortingEnabled(True)
            tv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            tv.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        tabs.addTab(self._tv_genp, "Kayıtlar (genp / backup)")
        tabs.addTab(self._tv_inet, "İnternet şifreleri (inet)")
        root.addWidget(tabs, 1)

        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Hazır — destek: keychain .db + backup_keychain_v2.plist")

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"{APP_NAME} — veritabanı seç",
            "",
            "Keychain (*.db *.sqlite *.plist);;SQLite (*.db *.sqlite);;Plist (*.plist);;Tüm dosyalar (*)",
        )
        if path:
            self._path_edit.setText(path)

    def _set_busy(self, busy: bool) -> None:
        self._btn_run.setEnabled(not busy)
        self._path_edit.setReadOnly(busy)
        self.setCursor(Qt.CursorShape.WaitCursor if busy else Qt.CursorShape.ArrowCursor)

    def _start_decrypt(self) -> None:
        path = self._path_edit.text().strip()
        if not path:
            QMessageBox.warning(
                self,
                APP_NAME,
                "Lütfen bir dosya yolu girin veya dosya seçin.",
            )
            return
        err = validate_keychain_file(path)
        if err:
            QMessageBox.warning(self, APP_NAME, err)
            return

        if self._worker and self._worker.isRunning():
            QMessageBox.information(self, APP_NAME, "Çözümleme zaten devam ediyor.")
            return

        self._worker = DecryptWorker(path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._on_worker_finished)

        self._set_busy(True)
        self._progress.setValue(0)
        self.statusBar().showMessage("Çalışıyor…")
        self._btn_export.setEnabled(False)
        self._data = None
        self._model_genp.set_records([])
        self._model_inet.set_records([])
        self._worker.start()

    def _on_progress(self, message: str, value: int) -> None:
        self.statusBar().showMessage(message)
        if 0 <= value <= 100:
            self._progress.setValue(value)

    def _on_finished(self, data: dict) -> None:
        self._data = data
        genp = [x for x in (data.get("genp") or []) if isinstance(x, dict) and x]
        inet = [x for x in (data.get("inet") or []) if isinstance(x, dict) and x]
        self._model_genp.set_records(genp)
        self._model_inet.set_records(inet)
        self._btn_export.setEnabled(True)
        src = data.get("source", "sqlite")
        self.statusBar().showMessage(
            f"Bitti ({src}) — kayıtlar: {len(genp)}, inet: {len(inet)}"
        )

    def _on_failed(self, msg: str) -> None:
        QMessageBox.critical(self, APP_NAME, msg)
        self.statusBar().showMessage("Hata.")

    def _on_worker_finished(self) -> None:
        self._set_busy(False)

    def _export_db(self) -> None:
        if not self._data:
            QMessageBox.warning(self, APP_NAME, "Önce analiz / çözümleme çalıştırın.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            f"{APP_NAME} — SQLite kaydet",
            "decrypted_keychain.db",
            "SQLite (*.db)",
        )
        if not path:
            return
        src = self._path_edit.text().strip()
        try:
            export_keychain_to_sqlite(src, path, self._data)
        except Exception as exc:
            QMessageBox.critical(self, APP_NAME, str(exc))
            return
        QMessageBox.information(self, APP_NAME, f"Dosya kaydedildi:\n{path}")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("dYKcrpytor")
    app.setStyleSheet(APP_STYLESHEET)
    icon_path = icon_png_path()
    if icon_path is not None:
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
    win = MainWindow()
    if icon_path is not None:
        win.setWindowIcon(QIcon(str(icon_path)))
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
