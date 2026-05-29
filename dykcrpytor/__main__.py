# python -m dykcrpytor

from __future__ import annotations

from dykcrpytor.qt_bootstrap import configure_qt_plugin_paths, ensure_project_on_path


def main() -> None:
    ensure_project_on_path()
    configure_qt_plugin_paths()
    from dykcrpytor.gui.main_window import main as run_app

    run_app()


if __name__ == "__main__":
    main()
