# LAN Chat

A minimal, real-time chat application for devices on the same local network.  
No internet, no accounts, no database — just WebSockets over your LAN.

---

## Installation

```bash
# 1. Clone or copy the project
cd LAN_Chat

# 2. (Recommended) Create a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Server

```bash
python server.py
```

or

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

On startup the server prints the LAN IP address, for example:

```
  Open in browser:  http://192.168.1.42:8000
```

---

## Connecting from Another Device

1. Make sure both devices are on the **same Wi-Fi / LAN**.
2. Open a browser on the second device and navigate to:

```
http://<HOST_IP>:8000
```

Replace `<HOST_IP>` with the address printed by the server.

---

## Finding Your LAN IP Manually

| OS      | Command                         |
|---------|---------------------------------|
| Windows | `ipconfig`                      |
| Linux   | `ip addr show` or `hostname -I` |
| macOS   | `ifconfig en0`                  |

Look for an address like `192.168.x.x` or `10.x.x.x`.

---

## Troubleshooting

### Windows Firewall

If other devices cannot connect:

1. Open **Windows Defender Firewall → Advanced Settings**.
2. **Inbound Rules → New Rule → Port → TCP 8000 → Allow**.
3. Or temporarily disable the firewall for testing.

Alternatively, run in an elevated PowerShell:

```powershell
New-NetFirewallRule -DisplayName "LAN Chat" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Linux Firewall (ufw)

```bash
sudo ufw allow 8000/tcp
```

### macOS Firewall

1. **System Settings → Network → Firewall → Options**.
2. Add Python (or the terminal app) to the allow list.

Or disable the firewall temporarily:

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

### Devices Not on the Same Subnet

Both devices must share the same network prefix (e.g., `192.168.1.x`).  
If one device is on `192.168.0.x` and the other on `192.168.1.x`, they cannot see each other without router configuration.

Common fixes:

- Connect both devices to the **same Wi-Fi network**.
- Avoid guest networks — they often isolate clients.
- Disable any VPN that might override the local route.

---

## Project Structure

```
LAN_Chat/
├── server.py            # FastAPI + WebSocket server
├── requirements.txt     # Python dependencies
├── README.md
├── templates/
│   └── index.html       # Chat page template
└── static/
    ├── style.css        # Minimal stylesheet
    └── script.js        # Client-side WebSocket logic
```

---

## License

This project is provided as-is for personal and educational use.
