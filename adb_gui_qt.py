#!/usr/bin/env python3
"""
ADB Connect - Native PyQt6 Desktop Application
Theme: Modern White Clean + Orange Accents (#FF6B00 / #FF8533)
Dev: TheFoolByte / rohandhika
Cross-platform: Linux (Wayland/X11) & Windows
"""

import os
import re
import subprocess
import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QMessageBox
)

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

class CommandWorker(QThread):
    finished_signal = pyqtSignal(int, str, str, str)

    def __init__(self, action, cmd):
        super().__init__()
        self.action = action
        self.cmd = cmd

    def run(self):
        code, out, err = run_cmd(self.cmd)
        self.finished_signal.emit(code, out, err, self.action)

class ADBConnectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADB Connect")
        self.setObjectName("ADBConnectWindow")
        self.setFixedSize(400, 610)
        self.worker = None

        self.init_ui()
        self.apply_styles()
        self.refresh_devices()
        self.auto_detect_ip()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # 1. Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        title = QLabel("⚡ ADB CONNECT")
        title.setObjectName("appTitle")
        subtitle = QLabel("Android Mirror & WiFi Controller")
        subtitle.setObjectName("appSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # 2. Section Devices
        sec_dev_header = QHBoxLayout()
        sec_dev_lbl = QLabel("TERHUBUNG")
        sec_dev_lbl.setObjectName("sectionLabel")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("btnSmall")
        self.btn_refresh.clicked.connect(self.refresh_devices)
        sec_dev_header.addWidget(sec_dev_lbl)
        sec_dev_header.addStretch()
        sec_dev_header.addWidget(self.btn_refresh)
        main_layout.addLayout(sec_dev_header)

        self.device_list = QListWidget()
        self.device_list.setObjectName("deviceList")
        self.device_list.setFixedHeight(75)
        main_layout.addWidget(self.device_list)

        # 3. Card USB
        card_usb = QFrame()
        card_usb.setObjectName("card")
        card_usb_layout = QVBoxLayout(card_usb)
        card_usb_layout.setContentsMargins(14, 12, 14, 12)
        card_usb_layout.setSpacing(6)

        lbl_usb = QLabel("MODE 1: USB KABEL")
        lbl_usb.setObjectName("cardTitle")
        self.btn_scrcpy_usb = QPushButton("🔌 Buka Scrcpy (USB)")
        self.btn_scrcpy_usb.setObjectName("btnPrimary")
        self.btn_scrcpy_usb.clicked.connect(lambda: self.launch_scrcpy("usb"))
        card_usb_layout.addWidget(lbl_usb)
        card_usb_layout.addWidget(self.btn_scrcpy_usb)
        main_layout.addWidget(card_usb)

        # 4. Card WiFi / Hotspot
        card_wifi = QFrame()
        card_wifi.setObjectName("card")
        card_wifi_layout = QVBoxLayout(card_wifi)
        card_wifi_layout.setContentsMargins(14, 12, 14, 12)
        card_wifi_layout.setSpacing(8)

        lbl_wifi = QLabel("MODE 2: WIFI / TETHERING HOTSPOT")
        lbl_wifi.setObjectName("cardTitle")
        card_wifi_layout.addWidget(lbl_wifi)

        self.btn_tcpip = QPushButton("📡 1. Buka Port 5555 (Colok USB Sekali)")
        self.btn_tcpip.setObjectName("btnSecondary")
        self.btn_tcpip.clicked.connect(self.enable_tcpip)
        card_wifi_layout.addWidget(self.btn_tcpip)

        ip_layout = QHBoxLayout()
        ip_layout.setSpacing(6)
        self.input_ip = QLineEdit()
        self.input_ip.setObjectName("inputIp")
        self.input_ip.setPlaceholderText("IP HP (cth: 192.168.100.60)")
        btn_detect = QPushButton("Detect")
        btn_detect.setObjectName("btnSmallDetect")
        btn_detect.clicked.connect(self.auto_detect_ip)
        ip_layout.addWidget(self.input_ip)
        ip_layout.addWidget(btn_detect)
        card_wifi_layout.addLayout(ip_layout)

        wifi_actions = QHBoxLayout()
        wifi_actions.setSpacing(8)
        self.btn_connect = QPushButton("🔗 2. Connect WiFi")
        self.btn_connect.setObjectName("btnSecondary")
        self.btn_connect.clicked.connect(self.connect_wifi)

        self.btn_scrcpy_wifi = QPushButton("📱 Buka Scrcpy")
        self.btn_scrcpy_wifi.setObjectName("btnOrange")
        self.btn_scrcpy_wifi.clicked.connect(lambda: self.launch_scrcpy("wifi"))

        wifi_actions.addWidget(self.btn_connect)
        wifi_actions.addWidget(self.btn_scrcpy_wifi)
        card_wifi_layout.addLayout(wifi_actions)

        main_layout.addWidget(card_wifi)

        # 5. Stop / Exit Actions
        stop_layout = QHBoxLayout()
        stop_layout.setSpacing(8)
        self.btn_stop_scrcpy = QPushButton("⏹ Stop Mirror")
        self.btn_stop_scrcpy.setObjectName("btnDanger")
        self.btn_stop_scrcpy.clicked.connect(self.stop_scrcpy)

        self.btn_disconnect_all = QPushButton("🔌 Disconnect All")
        self.btn_disconnect_all.setObjectName("btnSecondary")
        self.btn_disconnect_all.clicked.connect(self.disconnect_all)

        stop_layout.addWidget(self.btn_stop_scrcpy)
        stop_layout.addWidget(self.btn_disconnect_all)
        main_layout.addLayout(stop_layout)

        # 6. Status Footer
        self.status_bar = QLabel("Siap digunakan.")
        self.status_bar.setObjectName("statusText")
        main_layout.addWidget(self.status_bar)

    def apply_styles(self):
        style = """
        QWidget {
            background-color: #F8F9FA;
            color: #2D3142;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 13px;
        }

        #appTitle {
            font-size: 18px;
            font-weight: 800;
            color: #FF6B00;
            letter-spacing: 0.5px;
        }

        #appSubtitle {
            font-size: 11px;
            color: #8D99AE;
            font-weight: 500;
        }

        #sectionLabel {
            font-size: 10px;
            font-weight: 700;
            color: #8D99AE;
            letter-spacing: 1px;
        }

        #card {
            background-color: #FFFFFF;
            border: 1px solid #E9ECEF;
            border-radius: 12px;
        }

        #cardTitle {
            font-size: 10px;
            font-weight: 700;
            color: #FF6B00;
            letter-spacing: 0.8px;
        }

        #deviceList {
            background-color: #FFFFFF;
            border: 1px solid #E9ECEF;
            border-radius: 10px;
            padding: 4px;
        }

        #deviceList::item {
            padding: 6px 10px;
            border-radius: 6px;
            margin-bottom: 2px;
            background-color: #F8F9FA;
            color: #2D3142;
            font-weight: 600;
        }

        #inputIp {
            background-color: #FFFFFF;
            border: 1px solid #DEE2E6;
            border-radius: 8px;
            padding: 7px 10px;
            color: #2D3142;
            font-size: 12px;
            selection-background-color: #FF6B00;
        }

        #inputIp:focus {
            border: 1px solid #FF6B00;
        }

        QPushButton {
            border: none;
            border-radius: 8px;
            padding: 9px 14px;
            font-weight: 600;
            font-size: 12px;
        }

        #btnPrimary {
            background-color: #FFFFFF;
            border: 1.5px solid #FF6B00;
            color: #FF6B00;
        }
        #btnPrimary:hover {
            background-color: #FFF2E8;
        }
        #btnPrimary:pressed {
            background-color: #FFE5D1;
        }

        #btnOrange {
            background-color: #FF6B00;
            color: #FFFFFF;
        }
        #btnOrange:hover {
            background-color: #E65A00;
        }
        #btnOrange:pressed {
            background-color: #CC5000;
        }

        #btnSecondary {
            background-color: #F1F3F5;
            color: #495057;
            border: 1px solid #E9ECEF;
        }
        #btnSecondary:hover {
            background-color: #E9ECEF;
            color: #212529;
        }

        #btnDanger {
            background-color: #FFF5F5;
            color: #E03131;
            border: 1px solid #FFC9C9;
        }
        #btnDanger:hover {
            background-color: #FFE3E3;
            color: #C92A2A;
            border-color: #FFA8A8;
        }
        #btnDanger:pressed {
            background-color: #FFC9C9;
        }

        #btnSmall, #btnSmallDetect {
            background-color: #FFFFFF;
            border: 1px solid #DEE2E6;
            color: #495057;
            padding: 4px 10px;
            font-size: 11px;
            border-radius: 6px;
        }
        #btnSmall:hover, #btnSmallDetect:hover {
            background-color: #F1F3F5;
            border-color: #CED4DA;
        }

        #statusText {
            font-size: 11px;
            color: #6C757D;
            padding-left: 2px;
        }
        """
        self.setStyleSheet(style)

    def refresh_devices(self):
        self.device_list.clear()
        code, out, _ = run_cmd("adb devices -l")
        devices = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                status = parts[1]
                t = "WIFI" if ":" in serial else "USB"
                devices.append((serial, t, status))

        if not devices:
            it = QListWidgetItem("Belum ada perangkat yang terhubung.")
            it.setFlags(Qt.ItemFlag.NoItemFlags)
            self.device_list.addItem(it)
        else:
            for s, t, stat in devices:
                it = QListWidgetItem(f"📱 {s}  [{t}]  •  {stat}")
                self.device_list.addItem(it)

    def enable_tcpip(self):
        self.status_bar.setText("Mengaktifkan port 5555 di HP...")
        self.btn_tcpip.setEnabled(False)

        def done(code, out, err, _):
            self.btn_tcpip.setEnabled(True)
            if code == 0:
                self.status_bar.setText("✓ Port 5555 aktif! Kabel USB boleh dicabut.")
                self.auto_detect_ip()
            else:
                self.status_bar.setText(f"Gagal buka port: {err or out}")

        self.worker = CommandWorker("tcpip", "adb tcpip 5555")
        self.worker.finished_signal.connect(done)
        self.worker.start()

    def auto_detect_ip(self):
        self.status_bar.setText("Mencari IP HP...")
        code, out, _ = run_cmd("adb shell ip -f inet addr show wlan0")
        ip = None
        if code == 0:
            m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", out)
            if m:
                ip = m.group(1)
        if not ip:
            code, out, _ = run_cmd("adb shell ip route")
            if code == 0:
                for line in out.splitlines():
                    if "wlan0" in line or "link" in line:
                        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                        if m:
                            ip = m.group(1)
                            break
        if ip:
            self.input_ip.setText(ip)
            self.status_bar.setText(f"✓ IP HP ditemukan: {ip}")
        else:
            self.status_bar.setText("IP tidak terdeteksi otomatis. Masukkan manual.")

    def connect_wifi(self):
        ip = self.input_ip.text().strip()
        if not ip:
            self.status_bar.setText("Masukkan IP HP terlebih dahulu!")
            return

        self.status_bar.setText(f"Menghubungkan ke {ip}:5555...")
        self.btn_connect.setEnabled(False)

        def done(code, out, err, _):
            self.btn_connect.setEnabled(True)
            msg = out or err
            self.status_bar.setText(msg)
            self.refresh_devices()

        self.worker = CommandWorker("connect", f"adb connect {ip}:5555")
        self.worker.finished_signal.connect(done)
        self.worker.start()

    def get_device_resolution(self):
        code, out, _ = run_cmd("adb shell wm size")
        if code == 0:
            m = re.search(r"Physical size:\s*(\d+)x(\d+)", out)
            if m:
                w, h = int(m.group(1)), int(m.group(2))
                return w, h
        return None, None

    def calculate_adaptive_window_size(self):
        screen_h = 1080
        screen_w = 1920
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_h = screen.geometry().height()
                screen_w = screen.geometry().width()
        except Exception:
            pass

        # Target tinggi jendela: 70% dari tinggi layar laptop
        target_h = int(screen_h * 0.70)

        # Cek resolusi asli fisik HP via ADB
        w, h = self.get_device_resolution()
        if w and h and h > 0:
            aspect_ratio = w / h
            target_w = int(target_h * aspect_ratio)
        else:
            # Fallback jika ADB wm size tidak terbaca: rasio 9:19.5 smartphone modern
            target_w = int(target_h * (9 / 19.5))

        return max(320, target_w), max(500, target_h)

    def launch_scrcpy(self, mode="usb"):
        target_w, target_h = self.calculate_adaptive_window_size()
        flags = f"--no-audio --turn-screen-off --window-width={target_w} --window-height={target_h}"
        target = "-d" if mode == "usb" else "-e"
        cmd = f"scrcpy {target} {flags}"

        if sys.platform == "win32":
            subprocess.Popen(f"cmd /c start {cmd}", shell=True)
        else:
            # Gunakan script launcher agar Hyprland meng-assign class scrcpy ke floating rule
            subprocess.Popen(f"nohup {cmd} >/dev/null 2>&1 &", shell=True)

        self.status_bar.setText(f"✓ Scrcpy {mode.upper()} dibuka ({target_w}x{target_h}px auto-scale).")

    def stop_scrcpy(self):
        if sys.platform == "win32":
            run_cmd("taskkill /F /IM scrcpy.exe")
        else:
            run_cmd("pkill -9 scrcpy")
        self.status_bar.setText("✓ Mirror scrcpy dihentikan.")

    def disconnect_all(self):
        self.stop_scrcpy()
        run_cmd("adb disconnect")
        self.status_bar.setText("✓ Semua koneksi ADB WiFi terputus.")
        self.refresh_devices()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ADB Connect")
    window = ADBConnectApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
