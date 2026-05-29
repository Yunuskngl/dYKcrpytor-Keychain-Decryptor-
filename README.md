# dYKcrpytor

dYKcrpytor is an open-source desktop app for decrypting and analyzing iOS keychain data from `keychain-2.db` and `backup_keychain_v2.plist`. Features a PyQt6 GUI, tabular results, and SQLite export. Built for research and digital forensics workflows.

iOS keychain verisini çözen ve sonuçları tablo + SQLite dışa aktarımı ile sunan PyQt6 masaüstü uygulaması.

Çekirdek şifre çözme mantığı [xperylabhub/ios_keychain_decrypter](https://github.com/xperylabhub/ios_keychain_decrypter) temel alınarak uyarlanmıştır.

## Geliştirici çalıştırma

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run_gui.py
```

## Paketleme

| Platform | Komut | Çıktı |
|----------|--------|--------|
| macOS | `./build_macos_app.sh` | `dist/dYKcrpytor.app`, `dist/dYKcrpytor.dmg` |
| Windows | `build_windows.bat` | `dist\dYKcrpytor.exe` |

Uygulama ikonu: `assets/icons/access-keys.png`

GitHub Release ve yükleme rehberi: [RELEASE.md](RELEASE.md)

## Lisans

GNU General Public License v3.0 — bkz. [LICENSE](LICENSE).
