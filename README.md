<h1 align="center">⚡ ADB Connect</h1>

<p align="center">
  <strong>A modern desktop GUI controller for Android ADB & Wireless scrcpy Mirroring</strong>
</p>

<p align="center">
  <a href="https://github.com/TheFoolByte/adb-connect/releases/latest"><img src="https://img.shields.io/github/v/release/TheFoolByte/adb-connect?color=FF6B00&style=flat-square" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/GUI-PyQt6-brightgreen?style=flat-square" alt="PyQt6">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

<p align="center">
  <a href="README.md">English</a> • <a href="README(id).md">Bahasa Indonesia</a>
</p>

<p align="center">
  <img src="display.png" alt="ADB Connect Screenshot" width="400">
</p>

---

## 📖 Overview

**ADB Connect** is a clean, lightweight desktop GUI application built with **PyQt6**. It streamlines connecting Android devices via **USB** or **Wireless ADB (WiFi / Mobile Hotspot)** and provides instant **scrcpy** display mirroring with adaptive aspect-ratio scaling tailored to your desktop resolution.

---

## ✨ Features

- **🎨 Modern Card UI**: Minimalist white card interface with vibrant orange accents (`#FF6B00`) and dark theme desktop harmony.
- **🔍 Auto-Detect IP**: One-click detection for device IP across WiFi (`wlan0`), hotspot tethering (`ap0`), and secondary network interfaces.
- **📐 Adaptive Auto-Scaling**: Queries physical device resolution (`adb shell wm size`) and auto-scales the mirror window to ~70% of host monitor height—maintaining native aspect ratios without distortion.
- **🔄 Dual Connection Modes**:
  - **Mode 1 (USB Cable)**: One-click tethered display mirroring.
  - **Mode 2 (WiFi / Hotspot)**: Single USB-plug port `5555` initialization, wireless pairing, and cable-free mirroring.
- **🛑 Built-in Process Controls**: Single-click **Stop Mirror** (`pkill scrcpy` / `taskkill`) and **Disconnect All** (`adb disconnect`).
- **🪟 Tiling WM & Wayland Ready**: Native floating window integration for tiling window managers like Hyprland.

---

## 📦 Windows Installer & Releases

Pre-built binaries for Windows are available on [GitHub Releases](https://github.com/TheFoolByte/adb-connect/releases/latest):

| Package | Description |
| :--- | :--- |
| **`ADBConnect-Installer-x64.exe`** | Setup wizard that registers in Start Menu & Control Panel. |
| **`ADBConnect-Portable-x64.zip`** | Standalone portable bundle (no installation required). |

> *Note: Windows release bundles include standalone `adb` and `scrcpy` binaries.*

---

## 📋 Prerequisites (Linux)

Ensure you have Python 3.10+, ADB tools, and scrcpy installed:

### Arch Linux
```bash
sudo pacman -S android-tools scrcpy python-pyqt6
```

### Ubuntu / Debian
```bash
sudo apt install adb scrcpy python3-pyqt6
```

### Fedora
```bash
sudo dnf install android-tools scrcpy python3-pyqt6
```

---

## 🚀 Getting Started

### Run from Source
```bash
# Clone the repository
git clone https://github.com/TheFoolByte/adb-connect.git
cd adb-connect

# Launch the application
python3 adb_gui_qt.py
```

### Wireless Pairing Guide (WiFi / Hotspot)
1. Connect your Android device to PC via USB cable (ensure **USB Debugging** is enabled).
2. Click **`📡 1. Buka Port 5555`** to restart ADB in TCP/IP mode.
3. Click **`Detect`** to retrieve your phone's current IP address.
4. Unplug the USB cable.
5. Click **`🔗 2. Connect WiFi`** to pair wirelessly.
6. Click **`📱 Buka Scrcpy`** to launch wireless screen mirroring.

---

## ⚙️ Hyprland Integration (Optional)

To enable automatic floating behavior for ADB Connect and scrcpy in Hyprland, add these lines to `~/.config/hypr/configs/rules.lua` or `hyprland.conf`:

```lua
hl.window_rule({ match = { class = "^(scrcpy)$" }, float = 1, center = 1 })
hl.window_rule({ match = { class = "^(ADBConnectWindow)$" }, float = 1, center = 1 })
```

---

## 👤 Author

- GitHub: [@TheFoolByte](https://github.com/TheFoolByte)
- Repository: [TheFoolByte/adb-connect](https://github.com/TheFoolByte/adb-connect)
