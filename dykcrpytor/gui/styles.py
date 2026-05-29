# Application-wide Qt stylesheet.

APP_NAME = "dYKcrpytor"

APP_STYLESHEET = """
QMainWindow {
    background-color: #eef1f6;
}

QWidget#centralRoot {
    background-color: #eef1f6;
}

QLabel#appTitle {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #0f172a;
}

QLabel#appSubtitle {
    font-size: 13px;
    color: #64748b;
    margin-top: 2px;
}

QFrame#heroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1e3a5f, stop:1 #0f172a);
    border-radius: 14px;
    border: 1px solid #1e293b;
}

QLabel#heroTitle {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f8fafc;
}

QLabel#heroTagline {
    font-size: 12px;
    color: #94a3b8;
}

QFrame#panelCard {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

QLabel#sectionLabel {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
}

QLineEdit {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 13px;
    color: #0f172a;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #3b82f6;
    background-color: #ffffff;
}

QLineEdit:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
}

QPushButton {
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
}

QPushButton#primaryButton:hover:enabled {
    background-color: #1d4ed8;
}

QPushButton#primaryButton:pressed:enabled {
    background-color: #1e40af;
}

QPushButton#secondaryButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
}

QPushButton#secondaryButton:hover:enabled {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton#accentOutline {
    background-color: transparent;
    color: #2563eb;
    border: 1px solid #93c5fd;
}

QPushButton#accentOutline:hover:enabled {
    background-color: #eff6ff;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
    border-color: #e2e8f0;
}

QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #e2e8f0;
    min-height: 8px;
    max-height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    border-radius: 6px;
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3b82f6, stop:1 #6366f1);
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    top: -1px;
    background-color: #ffffff;
    padding: 4px;
}

QTabBar::tab {
    background-color: transparent;
    color: #64748b;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-bottom-color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
    color: #334155;
}

QTableView {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    gridline-color: #e2e8f0;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    selection-background-color: #dbeafe;
    selection-color: #1e3a8a;
}

QTableView::item {
    padding: 6px 8px;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 12px;
}

QHeaderView::section:first {
    border-top-left-radius: 8px;
}

QScrollBar:vertical {
    width: 10px;
    background: #f1f5f9;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar:horizontal {
    height: 10px;
    background: #f1f5f9;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 5px;
    min-width: 28px;
}

QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    font-size: 12px;
}

QFrame#infoStrip {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 2px;
}

QLabel#infoStripText {
    color: #1e40af;
    font-size: 12px;
    padding: 8px 12px;
}
"""
