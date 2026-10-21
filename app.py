#!/usr/bin/env python3
"""
ADB Connect - Cross-platform Android screen mirror & ADB helper
Dev: TheFoolByte / rohandhika
Supports: Linux & Windows
"""

import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import webbrowser

PORT = 5055

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
                "type": "wifi" if ":" in parts[0] else "usb",
                "info": " ".join(parts[2:]) if len(parts) > 2 else ""
            })
    return devices

def get_device_ip():
    # Try getting IP via wlan0
    code, out, _ = run_cmd("adb shell ip -f inet addr show wlan0")
    if code == 0:
        m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", out)
        if m:
            return m.group(1)
    # Fallback to ip route
    code, out, _ = run_cmd("adb shell ip route")
    if code == 0:
        for line in out.splitlines():
            if "wlan0" in line or "link" in line:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if m:
                    return m.group(1)
    return None

def launch_scrcpy(target=""):
    flags = "--no-audio --turn-screen-off"
    if target:
        if ":" in target:
            cmd = f"scrcpy -e {flags}"
        else:
            cmd = f"scrcpy -d {flags}"
    else:
        cmd = f"scrcpy {flags}"
    
    # Detach process so server doesn't block
    if sys.platform == "win32":
        subprocess.Popen(f"cmd /c start {cmd}", shell=True)
    else:
        subprocess.Popen(f"nohup {cmd} >/dev/null 2>&1 &", shell=True)
    return True

HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ADB Connect · Vanguard</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
body { background: #0f111a; color: #e1e4eb; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
.card { background: #181b28; border: 1px solid #282d42; border-radius: 16px; width: 100%; max-width: 480px; padding: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
.header { text-align: center; margin-bottom: 24px; }
.header h1 { font-size: 22px; color: #00e5ff; letter-spacing: 1px; margin-bottom: 6px; }
.header p { font-size: 13px; color: #8892b0; }
.section { background: #12141f; border: 1px solid #1f2335; border-radius: 10px; padding: 14px; margin-bottom: 16px; }
.section-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #7aa2f7; margin-bottom: 10px; font-weight: bold; }
.device-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; background: #1a1e30; border-radius: 6px; margin-bottom: 6px; font-size: 13px; }
.badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: bold; text-transform: uppercase; }
.badge-usb { background: #00e5ff22; color: #00e5ff; border: 1px solid #00e5ff44; }
.badge-wifi { background: #9d7cd822; color: #bb9af7; border: 1px solid #bb9af744; }
.badge-offline { background: #f7768e22; color: #f7768e; border: 1px solid #f7768e44; }
.btn { display: block; width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer; transition: all 0.2s; margin-bottom: 8px; text-align: center; }
.btn-primary { background: #00e5ff; color: #0f111a; }
.btn-primary:hover { background: #33ebff; transform: translateY(-1px); }
.btn-secondary { background: #24283b; color: #c0caf5; border: 1px solid #3b4261; }
.btn-secondary:hover { background: #2f354f; }
.btn-scrcpy { background: linear-gradient(135deg, #7aa2f7, #bb9af7); color: #0f111a; }
.btn-scrcpy:hover { opacity: 0.9; transform: translateY(-1px); }
.input-group { display: flex; gap: 8px; margin-bottom: 8px; }
.input-group input { flex: 1; background: #1a1e30; border: 1px solid #282d42; border-radius: 6px; padding: 10px 12px; color: #fff; font-size: 13px; outline: none; }
.input-group input:focus { border-color: #00e5ff; }
.status-log { font-family: monospace; font-size: 11px; color: #a9b1d6; background: #0b0c13; padding: 10px; border-radius: 6px; max-height: 90px; overflow-y: auto; white-space: pre-wrap; margin-top: 10px; }
.footer { text-align: center; font-size: 11px; color: #565f89; margin-top: 16px; }
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>⚡ ADB CONNECT</h1>
    <p>Android USB & WiFi Controller · Scrcpy</p>
  </div>

  <div class="section">
    <div class="section-title">Devices Terdeteksi</div>
    <div id="deviceList"><p style="font-size:12px;color:#565f89;text-align:center;">Memeriksa device...</p></div>
    <button class="btn btn-secondary" onclick="loadDevices()" style="padding:6px;font-size:12px;margin-top:6px;margin-bottom:0;">🔄 Refresh Devices</button>
  </div>

  <div class="section">
    <div class="section-title">Mode 1: USB Mirror</div>
    <button class="btn btn-primary" onclick="mirrorUsb()">🔌 Buka Scrcpy (USB)</button>
  </div>

  <div class="section">
    <div class="section-title">Mode 2: WiFi / Hotspot Tethering</div>
    <p style="font-size:11px;color:#8892b0;margin-bottom:10px;">Colok USB sekali → klik Setup WiFi → cabut USB → Connect WiFi.</p>
    <button class="btn btn-secondary" onclick="setupWifi()">📡 1. Enable Port 5555 (via USB)</button>
    <div class="input-group">
      <input type="text" id="ipInput" placeholder="IP HP (contoh: 192.168.100.60)">
      <button class="btn btn-secondary" onclick="detectIp()" style="width:auto;margin:0;padding:0 12px;font-size:12px;">Detect</button>
    </div>
    <button class="btn btn-secondary" onclick="connectWifi()">🔗 2. Connect ADB WiFi</button>
    <button class="btn btn-scrcpy" onclick="mirrorWifi()" style="margin-top:8px;">📱 Buka Scrcpy (WiFi)</button>
  </div>

  <div class="section" style="margin-bottom:0;">
    <div class="section-title">Log Status</div>
    <div class="status-log" id="logBox">Siap...</div>
  </div>

  <div class="footer">Dev: TheFoolByte · Vanguard Edition</div>
</div>

<script>
function log(msg) {
  const box = document.getElementById('logBox');
  box.textContent = msg + '\\n' + box.textContent;
}

async function api(path, data={}) {
  const res = await fetch(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  return await res.json();
}

async function loadDevices() {
  const r = await api('/api/devices');
  const el = document.getElementById('deviceList');
  if (!r.devices || r.devices.length === 0) {
    el.innerHTML = '<p style="font-size:12px;color:#f7768e;text-align:center;">Tidak ada device terhubung</p>';
    return;
  }
  el.innerHTML = r.devices.map(d => `
    <div class="device-item">
      <span><strong>${d.serial}</strong></span>
      <span class="badge badge-${d.type}">${d.type}</span>
    </div>
  `).join('');
}

async function mirrorUsb() {
  log('Membuka scrcpy via USB...');
  const r = await api('/api/scrcpy', {mode: 'usb'});
  log(r.msg);
}

async function setupWifi() {
  log('Mengaktifkan port TCP/IP 5555...');
  const r = await api('/api/tcpip');
  log(r.msg);
  detectIp();
}

async function detectIp() {
  log('Mencari IP HP...');
  const r = await api('/api/detect-ip');
  if (r.ip) {
    document.getElementById('ipInput').value = r.ip;
    log('IP HP ditemukan: ' + r.ip);
  } else {
    log('Gagal deteksi IP otomatis. Masukkan manual.');
  }
}

async function connectWifi() {
  const ip = document.getElementById('ipInput').value.trim();
  if (!ip) { log('Error: Masukkan IP HP dulu'); return; }
  log('Menghubungkan ke ' + ip + ':5555...');
  const r = await api('/api/connect', {ip: ip});
  log(r.msg);
  loadDevices();
}

async function mirrorWifi() {
  log('Membuka scrcpy via WiFi...');
  const r = await api('/api/scrcpy', {mode: 'wifi'});
  log(r.msg);
}

window.onload = () => { loadDevices(); detectIp(); };
</script>
</body>
</html>
"""

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Quiet mode

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        res = {"status": "ok"}

        if self.path == "/api/devices":
            res["devices"] = get_devices()

        elif self.path == "/api/tcpip":
            code, out, err = run_cmd("adb tcpip 5555")
            res["msg"] = "Port 5555 dibuka. Sekarang kabel USB boleh dicabut!" if code == 0 else f"Error: {err}"

        elif self.path == "/api/detect-ip":
            ip = get_device_ip()
            res["ip"] = ip
            res["msg"] = f"IP: {ip}" if ip else "Tidak dapat mendeteksi IP otomatis"

        elif self.path == "/api/connect":
            ip = data.get("ip", "").strip()
            if ip:
                code, out, err = run_cmd(f"adb connect {ip}:5555")
                res["msg"] = out if code == 0 else f"Error: {err}"
            else:
                res["msg"] = "IP kosong"

        elif self.path == "/api/scrcpy":
            mode = data.get("mode", "")
            target = "-d" if mode == "usb" else "-e"
            launch_scrcpy(target)
            res["msg"] = f"Scrcpy dibuka ({mode}) dengan layar HP mati & no-audio."

        else:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode("utf-8"))

def main():
    print(f"\\n⚡ ADB Connect Web UI berjalan di: http://localhost:{PORT}")
    print("Tekan Ctrl+C untuk keluar.\\n")
    webbrowser.open(f"http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nServer dimatikan.")

if __name__ == "__main__":
    main()
