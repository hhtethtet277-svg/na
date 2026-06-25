import re
import requests
import base64
import os
import json
import asyncio
import ping3
from ping3 import ping
import time
from urllib.parse import urlparse, parse_qs

CONFIG_FILE = "config_kuranomistable.json"

# ==================== FIXED URL ====================
FIXED_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=984a6b9d9816&gw_sn=H1TA1EN000844&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.224&mac=ba:82:56:38:3c:e4&slot_num=14&nasip=192.168.1.95&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C142&chap_challenge=%5C231%5C120%5C061%5C135%5C144%5C056%5C264%5C325%5C247%5C143%5C047%5C046%5C332%5C375%5C215%5C356"
# ===================================================

# Color codes
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
w = "\033[0m"
c = "\033[1;36m"

auto_loop_running = False

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    print("\033[1;31m" + "="*56)
    print("\033[1;31m  ██████╗ ███████╗██╗  ██╗ ██████╗      ██╗  ██╗\033[0m")
    print("\033[1;31m  ██╔══██╗██╔════╝██║  ██║██╔═══██╗    ██║ ██╔╝\033[0m")
    print("\033[1;31m  ██████╔╝███████╗███████║██║   ██║    █████╔╝ \033[0m")
    print("\033[1;31m  ██╔══██╗╚════██║██╔══██║██║   ██║    ██╔═██╗ \033[0m")
    print("\033[1;31m  ██║  ██║███████║██║  ██║╚██████╔╝    ██║  ██╗\033[0m")
    print("\033[1;31m  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝     ╚═╝  ╚═╝\033[0m")
    print("\033[1;31m" + "="*56 + "\033[0m")
    print("\033[1;36m          RSHO Ka - WiFi Bypass Super Stable \033[0m")
    print("\033[1;31m" + "="*56 + "\033[0m")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(voucher):
    config = {"voucher": voucher}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def extract_from_url(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    mac = params.get('mac', [''])[0]
    gw_ip = params.get('gw_address', [''])[0]
    return mac, gw_ip

def replace_mac(url, new_mac):
    url = re.sub(r'(?<=mac=)[^&]+', new_mac, url)       
    return url

def get_session_id(session_url, mac_address):
    final_url = replace_mac(session_url, mac_address)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    }
    try:
        response = requests.get(final_url, headers=headers, timeout=10)
        session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response.url).group(1)
        return session_id
    except Exception:
        return None

def login_voucher(session_id, voucher):
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    headers = {"content-type": "application/json", "user-agent": "Mozilla/5.0"}
    try:
        response = requests.post(post_url, json=data, headers=headers, timeout=10)
        token_match = re.search('token=(.*?)&', response.text)
        if token_match:
            return token_match.group(1)
    except Exception:
        return None
    return None

async def check_internet():
    try:
        ping_result = await asyncio.to_thread(ping, "8.8.8.8", timeout=3)
        return ping_result is not None and ping_result is not False
    except:
        return False

def do_bypass(session_url, mac_address, voucher, gateway_ip):
    session_id = get_session_id(session_url, mac_address)
    if not session_id: return False
    active_session_id = login_voucher(session_id, voucher)
    if not active_session_id: return False
    
    try:
        requests.get(f'http://{gateway_ip}:2060/wifidog/auth?', params={'token': active_session_id, 'phoneNumber': 'RSHOUser'}, timeout=5)
        return True
    except:
        return False

async def auto_loop_bypass(session_url, mac_address, voucher, gateway_ip):
    global auto_loop_running
    auto_loop_running = True
    print(f"\n{c}[*] Auto-Bypass စနစ် စတင်ပြီ (လိုင်းပြုတ်မှသာ ပြန်ဝင်ပါမည်){w}\n")
    
    while auto_loop_running:
        is_connected = await check_internet()
        if not is_connected:
            print(f"{r}[!] အင်တာနက် ပြတ်တောက်သွားသည်! ပြန်ချိတ်နေသည်...{w}")
            if do_bypass(session_url, mac_address, voucher, gateway_ip):
                print(f"{g}[✓] အင်တာနက် ပြန်လည်ရရှိပါပြီ။{w}")
            else:
                print(f"{r}[-] ချိတ်ဆက်မှု မအောင်မြင်ပါ။{w}")
        await asyncio.sleep(30)

def start_bypass():
    clear_screen()
    banner()
    mac_address, gateway_ip = extract_from_url(FIXED_URL)
    config = load_config()
    old_voucher = config.get("voucher", "")
    voucher = input(f"\033[1;32m=> Voucher Code ထည့်ပါ ({old_voucher}): \033[0m").strip() or old_voucher
    save_config(voucher)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(auto_loop_bypass(FIXED_URL, mac_address, voucher, gateway_ip))
    except KeyboardInterrupt:
        print("\n\n  🛑 Auto loop stopped.")

if __name__ == "__main__":
    start_bypass()
