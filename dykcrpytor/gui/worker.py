# Background decrypt thread.

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal


class DecryptWorker(QThread):
    progress = pyqtSignal(str, int)
    finished_ok = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, keychain_path: str):
        super().__init__()
        self.keychain_path = keychain_path

    def run(self) -> None:
        try:
            from dykcrpytor.keychain.service import decrypt_keychain_file

            def on_progress(message: str, value=None):
                self.progress.emit(message, int(value) if value is not None else -1)

            data = decrypt_keychain_file(self.keychain_path, on_progress)
            self.finished_ok.emit(data)
        except Exception as exc:
            self.failed.emit(str(exc))
