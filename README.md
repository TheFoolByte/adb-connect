# ⚡ ADB Connect

A modern PyQt6 desktop GUI controller to connect Android devices to PC via USB or Wireless ADB (WiFi/Hotspot), featuring one-click scrcpy screen mirroring with adaptive aspect-ratio scaling.

[English](README.md) | [Bahasa Indonesia](README(id).md)

---

## ✨ Features

- **Clean Card UI**: Minimalist white card layout (`#FFFFFF`) with vivid orange highlights (`#FF6B00`).
- **Multi-Interface IP Detection**: Automatically resolves device IP on standard WiFi (`wlan0`), Hotspot Tethering (`ap0`), and secondary mobile network interfaces.
- **Adaptive scrcpy Auto-Scaling**: Computes physical device resolution (`adb shell wm size`) against host display bounds (~70% monitor height) to maintain distortion-free native aspect ratios.
- **Dual Connection Workflow**:
  - **Mode 1 (USB Cable)**: Direct one-click tethered mirroring.
  - **Mode 2 (WiFi / Hotspot)**: Single USB-plug TCP/IP port 5555 setup, automatic IP discovery, wireless pairing, and cable-free mirroring.
- **Integrated Process Controls**: One-click *Stop Mirror* (`pkill scrcpy` / `taskkill`) and *Disconnect All* (`adb disconnect`).
- **Tiling WM & Wayland Ready**: Out-of-the-box floating rules for window managers like Hyprland.

---

## 📦 Windows Installer & Releases

Windows users can download automated binary packages directly from [GitHub Releases](https://github.com/TheFoolByte/adb-connect/releases):
- `ADBConnect-Installer-x64.exe` (Standard setup wizard registering in Start Menu & Control Panel).
- `ADBConnect-Portable-x64.zip` (Portable standalone zip).

---

## 📋 Prerequisites

- Python 3.10+
- `PyQt6`
- `android-tools` (`adb`)
- `scrcpy`

### Package Installation

**Arch Linux:**
```bash
sudo pacman -S android-tools scrcpy python-pyqt6
```

**Ubuntu / Debian:**
```bash
sudo apt install adb scrcpy python3-pyqt6
```

---

## 🚀 Usage

### Launching the Application
```bash
python3 adb_gui_qt.py
```

### Wireless Connection Workflow (WiFi / Hotspot)
1. Connect Android device via USB (ensure USB Debugging is enabled).
2. Click **`📡 1. Buka Port 5555`** to initialize TCP mode.
3. Click **`Detect`** to query device IP automatically.
4. Unplug the USB cable.
5. Click **`🔗 2. Connect WiFi`** to pair wirelessly.
6. Click **`📱 Buka Scrcpy`** to start screen mirroring.

---

## ⚙️ Hyprland Integration (Optional)

Add the following rules to your Hyprland configuration (`~/.config/hypr/configs/rules.lua` or `hyprland.conf`) to ensure floating window behavior:

```lua
hl.window_rule({ match = { class = "^(scrcpy)$" }, float = 1, center = 1 })
hl.window_rule({ match = { class = "^(ADBConnectWindow)$" }, float = 1, center = 1 })
```

---

## 👤 Author

- GitHub: [@TheFoolByte](https://github.com/TheFoolByte)
- Repository: [TheFoolByte/adb-connect](https://github.com/TheFoolByte/adb-connect)
