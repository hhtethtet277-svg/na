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

# Global variables for auto loop
auto_loop_running = False
loop_interval = 240  # 4 minute in seconds

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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'referer': final_url,
        'sec-ch-ua': '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0',
    }
    
    try:
        response = requests.get(final_url, headers=headers)
        session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response.url).group(1)
        return session_id
    except Exception as e:
        print(f"\033[1;31m[-] Error Getting Session ID: {e}\033[0m")
        return None

def login_voucher(session_id, voucher):
    data = {
        "accessCode": voucher,
        "sessionId": session_id,
        "apiVersion": 1
    }
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://portal-as.ruijienetworks.com",
        "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?RES=./../expand/res/mrlev58jlgslg49ervu&IS_EG=0&sessionId={session_id}",
        "user-agent": 'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/139.0.0.0',
    }
    try:
        with requests.post(post_url, json=data, headers=headers) as response:
            res_text = response.text
            token_match = re.search('token=(.*?)&', res_text)
            if token_match:
                return token_match.group(1), None
            else:
                return None, res_text
    except Exception as Error:
        print(f"\033[1;31m[-] Voucher Login Error: {Error}\033[0m")
        return None, str(Error)

async def get_smart_ping():
    targets = ["google.com", "8.8.8.8", "cloudflare.com"]
    print("\n" + "="*56)
    print("  📶 Checking Internet Connection...")
    print("="*56)
    connected = False
    best_result = None
    for target in targets:
        try:
            ping_result = await asyncio.to_thread(ping, target, timeout=2)
            if ping_result is not None:
                ping_ms = int(ping_result * 1000)
                connected = True
                print(f"  {g}✓{w} {target:15} → {g}{ping_ms:>4} ms{w}")
                best_result = f"{ping_ms} ms ({target})"
        except: continue
    print("="*56)
    return f"{g}Connected{w}" if connected else f"{r}Offline{w}"

def do_bypass(session_url, mac_address, voucher, gateway_ip):
    session_id = get_session_id(session_url, mac_address)
    if not session_id: return False
    active_session_id, error_msg = login_voucher(session_id, voucher)
    if not active_session_id: return False
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    params = {'token': active_session_id, 'phoneNumber': 'RSHOUser'}
    try:
        final_req_url = f'http://{gateway_ip}:2060/wifidog/auth?'
        requests.get(final_req_url, params=params, headers=headers)
        print("\n\033[1;32m[✓] Internet Bypass Successful!\033[0m")
        return True
    except:
        return False

async def auto_loop_bypass(session_url, mac_address, voucher, gateway_ip):
    global auto_loop_running
    auto_loop_running = True
    while auto_loop_running:
        do_bypass(session_url, mac_address, voucher, gateway_ip)
        await asyncio.sleep(loop_interval)

def start_bypass():
    clear_screen()
    banner()
    
    mac_address, gateway_ip = extract_from_url(FIXED_URL)
    config = load_config()
    old_voucher = config.get("voucher", "")
    
    print(f"\033[1;34m[+] Auto-Detected MAC: {mac_address}\033[0m")
    print(f"\033[1;34m[+] Auto-Detected Gateway IP: {gateway_ip}\033[0m\n")
    
    voucher = input(f"\033[1;32m=> Voucher Code ထည့်ပါ ({old_voucher}): \033[0m").strip() or old_voucher
    save_config(voucher)
    
    print("\n\033[1;33m[*] Internet Bypass စတင်နေပါပြီ...\033[0m")
    do_bypass(FIXED_URL, mac_address, voucher, gateway_ip)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(auto_loop_bypass(FIXED_URL, mac_address, voucher, gateway_ip))
    except KeyboardInterrupt:
        print("\n\n  🛑 Auto loop stopped.")

if __name__ == "__main__":
    start_bypass()
