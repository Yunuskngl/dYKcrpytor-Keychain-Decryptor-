# GitHub’a yükleme rehberi

## Repoya commit edilecekler (kaynak kod)

Tüm `Python_Decryptor/` klasörünü yükleyebilirsiniz; **şunlar hariç** (`.gitignore` zaten ayarlı):

| Dahil | Hariç |
|--------|--------|
| `dykcrpytor/`, `run_gui.py`, `scripts/` | `.venv/`, `.venv-win/`, `venv/` |
| `requirements.txt`, `*.spec` | `build/`, `dist/` |
| `assets/icons/access-keys.png` | Büyük test `.db` dosyaları (isterseniz) |
| `assets/icons/dYKcrpytor.icns`, `dYKcrpytor.ico` | |
| `build_macos_app.sh`, `build_windows.bat` | |

İkon dosyalarını repoda tutmak isteğe bağlıdır; macOS’ta `scripts/build_icons.py` her build’de yeniden üretebilir.

## GitHub Release’e eklenecekler (kullanıcı indirmeleri)

Kaynak kodu zip’lemek yerine **hazır paketleri** Release’e koyun:

| Platform | Dosya | Nasıl üretilir |
|----------|--------|----------------|
| macOS | `dYKcrpytor.dmg` | Mac’te `./build_macos_app.sh` |
| Windows | `dYKcrpytor.exe` | Windows’ta `build_windows.bat` |

`dist/` klasörünün tamamını repoya **yüklemeyin**; sadece Release ekleri olarak bu iki dosyayı (veya `.app` zip’ini) paylaşın.

## Adım adım

1. GitHub’da yeni repo oluşturun.
2. Yerelde:
   ```bash
   cd Python_Decryptor
   git init
   git add .
   git commit -m "Initial release: dYKcrpytor"
   git branch -M main
   git remote add origin https://github.com/KULLANICI/REPO.git
   git push -u origin main
   ```
3. macOS’ta: `./build_macos_app.sh` → `dist/dYKcrpytor.dmg`
4. Windows’ta: `build_windows.bat` → `dist\dYKcrpytor.exe`  
   (`.exe` yalnızca Windows’ta derlenir; Mac’ten cross-compile önerilmez.)
5. GitHub → **Releases** → **Draft a new release** → tag örn. `v1.0.0`
6. `dYKcrpytor.dmg` ve `dYKcrpytor.exe` dosyalarını sürükleyip yayınlayın.

## Notlar

- macOS ilk açılışta “tanınmıyor” uyarısı: Sağ tık → Aç veya `xattr -cr` + imzalama (`build_macos_app.sh` bunu dener).
- Lisans: GPL v2 (README’de belirtildiği gibi upstream ile uyumlu tutun).
