#!/usr/bin/env python3
"""
ADB Connect - TUI Floating Controller for Linux & Windows
Dev: TheFoolByte / rohandhika
"""

import os
import re
import subprocess
import sys
import time

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_CYAN = "\033[38;2;0;229;255m"
C_BLUE = "\033[38;2;122;162;247m"
C_PURPLE = "\033[38;2;187;154;247m"
C_GREEN = "\033[38;2;158;206;106m"
C_RED = "\033[38;2;247;118;142m"
C_MUTED = "\033[38;2;86;95;137m"
C_BG_CARD = "\033[48;2;24;27;40m"

def clear():
    os.system("cls" if sys.platform == "win32" else "clear")

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def get_devices():
    code, out, _ = run_cmd("adb devices -l")
    devices = []
    for line in out.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append({
                "serial": parts[0],
                "status": parts[1],
                "type": "WIFI" if ":" in parts[0] else "USB"
            })
    return devices

def get_device_ip():
    code, out, _ = run_cmd("adb shell ip -f inet addr show wlan0")
    if code == 0:
        m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", out)
        if m:
            return m.group(1)
    code, out, _ = run_cmd("adb shell ip route")
    if code == 0:
        for line in out.splitlines():
            if "wlan0" in line or "link" in line:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if m:
                    return m.group(1)
    return None

def launch_scrcpy(mode="usb"):
    flags = "--no-audio --turn-screen-off"
    target = "-d" if mode == "usb" else "-e"
    cmd = f"scrcpy {target} {flags}"
    if sys.platform == "win32":
        subprocess.Popen(f"cmd /c start {cmd}", shell=True)
    else:
        subprocess.Popen(f"nohup {cmd} >/dev/null 2>&1 &", shell=True)

def banner():
    print(f"{C_CYAN}  ⚡ {C_BOLD}ADB CONNECT{C_RESET} {C_MUTED}· Android Mirror Controller{C_RESET}")
    print(f"{C_MUTED}  ──────────────────────────────────────────{C_RESET}")

def show_devices(devices):
    print(f"  {C_BLUE}Devices Terdeteksi:{C_RESET}")
    if not devices:
        print(f"    {C_RED}• Tidak ada device terhubung{C_RESET}")
    else:
        for d in devices:
            tag = f"{C_CYAN}[USB]{C_RESET}" if d['type'] == 'USB' else f"{C_PURPLE}[WIFI]{C_RESET}"
            stat = f"{C_GREEN}{d['status']}{C_RESET}" if d['status'] == "device" else f"{C_RED}{d['status']}{C_RESET}"
            print(f"    • {d['serial']} {tag} ({stat})")
    print(f"{C_MUTED}  ──────────────────────────────────────────{C_RESET}")

def main():
    detected_ip = ""
    while True:
        clear()
        banner()
        devices = get_devices()
        show_devices(devices)

        print(f"  {C_BOLD}[1]{C_RESET} 🔌 Buka Scrcpy via {C_CYAN}USB{C_RESET} (layar HP mati)")
        print(f"  {C_BOLD}[2]{C_RESET} 📡 Buka Port 5555 ({C_BLUE}Colok USB dulu{C_RESET})")
        print(f"  {C_BOLD}[3]{C_RESET} 🔍 Deteksi IP HP Otomatis")
        print(f"  {C_BOLD}[4]{C_RESET} 🔗 Connect ADB via {C_PURPLE}WiFi / Hotspot{C_RESET}")
        print(f"  {C_BOLD}[5]{C_RESET} 📱 Buka Scrcpy via {C_PURPLE}WiFi{C_RESET} (layar HP mati)")
        print(f"  {C_BOLD}[6]{C_RESET} 🔄 Refresh Device List")
        print(f"  {C_BOLD}[0]{C_RESET} ❌ Keluar")
        print(f"{C_MUTED}  ──────────────────────────────────────────{C_RESET}")
        if detected_ip:
            print(f"  {C_GREEN}IP Tersimpan: {detected_ip}{C_RESET}")

        try:
            choice = input(f"  {C_CYAN}Pilih opsi (0-6): {C_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice == "1":
            print(f"  {C_GREEN}Meluncurkan scrcpy USB...{C_RESET}")
            launch_scrcpy("usb")
            time.sleep(1.5)
        elif choice == "2":
            print(f"  {C_BLUE}Mengaktifkan port 5555 via USB...{C_RESET}")
            code, out, err = run_cmd("adb tcpip 5555")
            if code == 0:
                print(f"  {C_GREEN}✓ Port 5555 aktif! Sekarang kabel USB boleh dicabut.{C_RESET}")
                detected_ip = get_device_ip() or detected_ip
                if detected_ip:
                    print(f"  {C_GREEN}✓ IP HP terdeteksi: {detected_ip}{C_RESET}")
            else:
                print(f"  {C_RED}Gagal: {err or out}{C_RESET}")
            input(f"\n  {C_MUTED}Tekan Enter untuk lanjut...{C_RESET}")
        elif choice == "3":
            print(f"  {C_BLUE}Mendeteksi IP HP...{C_RESET}")
            ip = get_device_ip()
            if ip:
                detected_ip = ip
                print(f"  {C_GREEN}✓ IP Ditemukan: {ip}{C_RESET}")
            else:
                print(f"  {C_RED}Gagal mendeteksi IP otomatis. Pastikan USB nyolok atau HP di WiFi/Hotspot.{C_RESET}")
            input(f"\n  {C_MUTED}Tekan Enter untuk lanjut...{C_RESET}")
        elif choice == "4":
            default_prompt = f" [{detected_ip}]" if detected_ip else ""
            ip = input(f"  Masukkan IP HP{default_prompt}: ").strip()
            if not ip and detected_ip:
                ip = detected_ip
            if ip:
                print(f"  {C_BLUE}Menghubungkan ke {ip}:5555...{C_RESET}")
                code, out, err = run_cmd(f"adb connect {ip}:5555")
                print(f"  {C_GREEN}{out or err}{C_RESET}")
                detected_ip = ip
            else:
                print(f"  {C_RED}IP tidak boleh kosong!{C_RESET}")
            time.sleep(2)
        elif choice == "5":
            print(f"  {C_GREEN}Meluncurkan scrcpy WiFi...{C_RESET}")
            launch_scrcpy("wifi")
            time.sleep(1.5)
        elif choice == "6":
            continue
        elif choice == "0":
            break

if __name__ == "__main__":
    main()
