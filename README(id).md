# ⚡ ADB Connect

GUI Controller desktop berbasis PyQt6 untuk menghubungkan perangkat Android ke PC via USB maupun Wireless ADB (WiFi/Hotspot), dilengkapi integrasi instan scrcpy display mirroring dengan auto-scaling adaptif.

[English](README.md) | [Bahasa Indonesia](README(id).md)

---

## ✨ Fitur Utama

- **GUI Card Modern**: Tampilan bersih dominan putih (`#FFFFFF`) dengan aksen oranye (`#FF6B00`).
- **Deteksi Otomatis Multi-Interface**: Mendukung deteksi IP perangkat di jaringan WiFi biasa (`wlan0`), Tethering Hotspot (`ap0`), maupun antarmuka sekunder.
- **Auto-Scale Adaptif scrcpy**: Menghitung resolusi fisik perangkat (`adb shell wm size`) terhadap resolusi monitor PC (tinggi ~70%), menjaga rasio aspek asli (bebas distorsi).
- **Dual Connection Mode**:
  - **Mode 1 (USB)**: Langsung jalankan mirror via kabel USB.
  - **Mode 2 (WiFi / Hotspot)**: Buka port TCP/IP 5555 sekali colok, deteksi IP, sambungkan wireless, dan jalankan mirror tanpa kabel.
- **Process Manager Terintegrasi**: Tombol *Stop Mirror* (`pkill scrcpy` / `taskkill`) dan *Disconnect All* (`adb disconnect`) dengan satu klik.
- **Wayland / Tiling WM Ready**: Dukungan floating window rule untuk Hyprland.

---

## 📋 Kebutuhan Sistem

- Python 3.10+
- `PyQt6`
- `android-tools` (`adb`)
- `scrcpy`

### Instalasi Dependensi

**Arch Linux:**
```bash
sudo pacman -S android-tools scrcpy python-pyqt6
```

**Ubuntu / Debian:**
```bash
sudo apt install adb scrcpy python3-pyqt6
```

---

## 🚀 Penggunaan

### Menjalankan Aplikasi
```bash
python3 adb_gui_qt.py
```

### Langkah Koneksi Wireless (WiFi / Hotspot)
1. Colokkan HP ke PC dengan kabel USB (aktifkan USB Debugging).
2. Klik tombol **`📡 1. Buka Port 5555`**.
3. Klik tombol **`Detect`** untuk mendeteksi IP HP secara otomatis.
4. Cabut kabel USB.
5. Klik **`🔗 2. Connect WiFi`**.
6. Klik **`📱 Buka Scrcpy`** untuk mulai mirroring layar.

---

## ⚙️ Integrasi Hyprland (Opsional)

Tambahkan baris berikut pada konfigurasi window rules Hyprland (`~/.config/hypr/configs/rules.lua` atau `hyprland.conf`) agar jendela aplikasi dan scrcpy otomatis melayang (floating):

```lua
hl.window_rule({ match = { class = "^(scrcpy)$" }, float = 1, center = 1 })
hl.window_rule({ match = { class = "^(ADBConnectWindow)$" }, float = 1, center = 1 })
```

---

## 👤 Author

- GitHub: [@TheFoolByte](https://github.com/TheFoolByte)
- Repository: [TheFoolByte/adb-connect](https://github.com/TheFoolByte/adb-connect)
