import base64, html, time, json, random, threading, os
from curl_cffi import requests
from headers import headers1, headers2, headers4, headers5, headers6
from utils import *
from solvers.rosolve import rs_get_token
from secure_auth import get_sa
from tempmail import get_email, get_inbox

SOLVER, API_KEY, TIMEOUT = validate_solver_config()

SOLVER_FUNCTIONS = {
    "rosolve": rs_get_token
}

MAX_CONSECUTIVE_CAPTCHA_FAILS = 30
MAX_CONSECUTIVE_CUSTOM_PASSWORD_FAILS = 3
MAX_CONSECUTIVE_INSUFFICIENT_BALANCE = 3

consecutive_captcha_fails = 0
consecutive_custom_password_fails = 0
consecutive_insufficient_balance = 0
captcha_fail_lock = threading.Lock()
custom_password_fail_lock = threading.Lock()
insufficient_balance_lock = threading.Lock()

EV_ENABLED_RUNTIME = False
DISPLAY_NAME_CFG_RUNTIME = {}

def set_runtime_options(ev_enabled, display_cfg):
    global EV_ENABLED_RUNTIME, DISPLAY_NAME_CFG_RUNTIME
    EV_ENABLED_RUNTIME = bool(ev_enabled)
    DISPLAY_NAME_CFG_RUNTIME = display_cfg if isinstance(display_cfg, dict) else {}

def thread_worker():
    global consecutive_captcha_fails, consecutive_custom_password_fails, consecutive_insufficient_balance, thread_restart_enabled
    while thread_restart_enabled:
        try:
            proxy_lines = load_proxies("input/proxies.txt")
            if not proxy_lines:
                tprint("No proxies available. Stopping all threads...")
                thread_restart_enabled = False
                threading.Thread(target=lambda: wait_for_threads_and_exit("No proxies available. All threads stopped.")).start()
                continue
            
            proxy = random.choice(proxy_lines)
            proxies = {
                "http": f"http://{proxy}", 
                "https": f"http://{proxy}"
            }

            session = requests.Session(
                impersonate="chrome", 
                proxies=proxies
            )
            
            response = session.get(url="https://www.roblox.com/", headers=headers1(), timeout=15)

            if response.status_code == 429:
                fprint(f"API rate limit hit! {response.url}")
                update_counter("failed")
                time.sleep(10)
                continue
            if "data-token=" in response.text:
                raw_token = response.text.split('data-token="')[1].split('"')[0]
                csrf_token = html.unescape(raw_token)

            username, basic_display_name = generate_username()
            birthday = generate_birthday()
            password = get_password()

            payload = {
                "username": username,
                "context": "Signup",
                "birthday": birthday
            }

            response = session.post(url="https://auth.roblox.com/v1/usernames/validate", headers=headers2(csrf_token), json=payload, timeout=15)

            if response.status_code != 200:
                if response.status_code == 403:
                    fprint("Token Validation Failed - likely caused by rotating proxy")
                    update_counter("failed")
                    continue
                elif response.status_code == 429:
                    fprint(f"API rate limit hit! {response.url}")
                    update_counter("failed")
                    time.sleep(10)
                    continue
                else:
                    fprint(f"Request failed with status code {response.status_code}: {response.text}")
                    update_counter("failed")
                    continue

            data = response.json()

            while data["message"] != "Username is valid" or response.status_code != 200:
                if data["message"] == "Token Validation Failed":
                    fprint("Token Validation Failed - likely caused by rotating proxy")
                else:
                    username, basic_display_name = generate_username()

                payload = {
                    "username": username,
                    "context": "Signup",
                    "birthday": birthday
                }

                response = session.post(url="https://auth.roblox.com/v1/usernames/validate", headers=headers2(csrf_token), json=payload, timeout=15)

                if response.status_code == 403:
                    csrf_token = response.headers.get('x-csrf-token')
                elif response.status_code == 429:
                    fprint(f"API rate limit hit! {response.url}")
                    time.sleep(10)
                    continue
                elif response.status_code != 200:
                    fprint(f"Request failed with status code {response.status_code}: {response.url}")
                    continue
                
                data = response.json()
                
            if not thread_restart_enabled:
                continue
            sprint(f"Account generation started: {username}")

            payload = {
                "username": username,
                "password": password
            }
            
            if not thread_restart_enabled:
                continue
            response = session.post(url="https://auth.roblox.com/v2/passwords/validate", headers=headers2(csrf_token), json=payload, timeout=15)
            data = response.json()

            if data["message"] != "Password is valid":
                config = load_config()
                if config.get("account_settings", {}).get("custom_password", {}).get("enabled", False):
                    with custom_password_fail_lock:
                        if consecutive_custom_password_fails >= MAX_CONSECUTIVE_CUSTOM_PASSWORD_FAILS:
                            continue
                        consecutive_custom_password_fails += 1
                        fprint(f"Custom password validation failed! ({consecutive_custom_password_fails}/{MAX_CONSECUTIVE_CUSTOM_PASSWORD_FAILS})")
                        update_counter("failed")
                        if consecutive_custom_password_fails == MAX_CONSECUTIVE_CUSTOM_PASSWORD_FAILS:
                            tprint(f"Too many consecutive custom password failures. Stopping all threads...")
                            thread_restart_enabled = False
                            threading.Thread(target=lambda: wait_for_threads_and_exit("Too many consecutive custom password failures. All threads stopped.")).start()
                    continue
                else:
                    fprint(f"Request failed with status code {response.status_code}: {response.url}")
                    update_counter("failed")
                    continue

            client_public_key, client_epoch_timestamp, server_nonce, sai_signature = get_sa(session)

            if not client_public_key:
                fprint("Unable to fetch server nonce.")
                update_counter("failed")
                continue

            signup_payload = {
                "username": username,
                "password": password,
                "birthday": birthday,
                "gender": 2,
                "isTosAgreementBoxChecked": True,
                "agreementIds": [
                    "306cc852-3717-4996-93e7-086daafd42f6",
                    "2ba6b930-4ba8-4085-9e8c-24b919701f15"
                ],
                "secureAuthenticationIntent": {
                    "clientPublicKey": client_public_key,
                    "clientEpochTimestamp": client_epoch_timestamp,
                    "serverNonce": server_nonce,
                    "saiSignature": sai_signature
                }
            }

            response = session.post(url="https://auth.roblox.com/v2/signup", headers=headers4(csrf_token, "auth.roblox.com"), json=signup_payload, timeout=15)
            data = json.loads(response.text)

            if data["errors"][0]["message"] != "Challenge is required to authorize the request":
                fprint("Pre-signup request failed")
                update_counter("failed")
                continue
            
            challenge_id = response.headers.get("rblx-challenge-id")
            challenge_metadata = response.headers.get("rblx-challenge-metadata")
            
            metadata = json.loads(base64.b64decode(challenge_metadata.encode("utf-8")).decode("utf-8"))

            blob = metadata.get("dataExchangeBlob")

            if not thread_restart_enabled:
                continue
                
            solver_func = SOLVER_FUNCTIONS[SOLVER]
            data, reason = solver_func(session, blob, proxy, API_KEY, TIMEOUT)

            if data == None:
                if "Insufficient solves" in reason:
                    with insufficient_balance_lock:
                        if consecutive_insufficient_balance >= MAX_CONSECUTIVE_INSUFFICIENT_BALANCE:
                            break
                        consecutive_insufficient_balance += 1
                        fprint(f"Failed to solve captcha: {reason}")
                        update_counter("failed")
                        if consecutive_insufficient_balance == MAX_CONSECUTIVE_INSUFFICIENT_BALANCE:
                            tprint("Captcha solver has no remaining balance to continue. Stopping all threads...")
                            thread_restart_enabled = False
                            threading.Thread(target=lambda: wait_for_threads_and_exit("Captcha solver has no remaining balance to continue. All threads stopped.")).start()
                    continue
                else:
                    with insufficient_balance_lock:
                        consecutive_insufficient_balance = 0
                    
                with captcha_fail_lock:
                    if consecutive_captcha_fails >= MAX_CONSECUTIVE_CAPTCHA_FAILS:
                        break
                    consecutive_captcha_fails += 1
                    fprint(f"Failed to solve captcha: {reason}")
                    update_counter("failed")
                    if consecutive_captcha_fails == MAX_CONSECUTIVE_CAPTCHA_FAILS:
                        tprint(f"Too many consecutive CAPTCHA failures ({consecutive_captcha_fails}). Stopping all threads...")
                        thread_restart_enabled = False
                        threading.Thread(target=lambda: wait_for_threads_and_exit("Too many consecutive CAPTCHA failures. All threads stopped.")).start()
                continue
                
            with captcha_fail_lock:
                consecutive_captcha_fails = 0
            with insufficient_balance_lock:
                consecutive_insufficient_balance = 0
            md = data.split("|")[0] + data.split("pk=A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F")[1].split("|cdn_url=")[0]
            caprint(f"Captcha solved: {md}")

            metadata = {
                "unifiedCaptchaId": challenge_id,
                "captchaToken": data,
                "actionType": "Signup"
            }

            payload = {
                "challengeId": challenge_id,
                "challengeType": "captcha",
                "challengeMetadata": json.dumps(metadata)
            }

            response = session.post(url="https://apis.roblox.com/challenge/v1/continue", headers=headers4(csrf_token, "apis.roblox.com"), json=payload, timeout=15)

            if response.status_code != 200:
                fprint(f"Request failed with status code {response.status_code}: {response.url}")
                update_counter("failed")
                continue

            encrypted_metadata = base64.b64encode(json.dumps(metadata).encode('utf-8')).decode('utf-8')

            response = session.post(url="https://auth.roblox.com/v2/signup", headers=headers5(encrypted_metadata, csrf_token, challenge_id), json=signup_payload, timeout=15)

            if response.status_code != 200:
                fprint(f"Request failed with status code {response.status_code}: {response.url}")
                update_counter("failed")
                continue
            
            data = response.json()
            user_id = data['userId']
            cookie = response.cookies['.ROBLOSECURITY']
            
            verified = False
            set_display_name = False
            email = None

            ev_enabled = EV_ENABLED_RUNTIME
            dn_cfg = DISPLAY_NAME_CFG_RUNTIME

            custom_display_name_enabled = False
            display_name = None
            if isinstance(dn_cfg, dict):
                custom_display_name_enabled = dn_cfg.get("enabled", False)
                mode = dn_cfg.get("mode", "custom")
                if custom_display_name_enabled:
                    if mode == "custom":
                        display_name = dn_cfg.get("custom_name", "").strip()
                        if not display_name:
                            wprint("Display name: custom mode selected but 'custom_name' is empty. Skipping display name update.")
                            custom_display_name_enabled = False
                    elif mode == "from_username":
                        display_name = basic_display_name
                    else:
                        custom_display_name_enabled = False

            need_csrf = ev_enabled or custom_display_name_enabled
            csrf_ready = True
            if need_csrf:
                response = session.get(url="https://www.roblox.com/home", headers=headers1(), timeout=15)
                if "data-token=" in response.text:
                    raw_token = response.text.split('data-token="')[1].split('"')[0]
                    csrf_token = html.unescape(raw_token)
                else:
                    wprint("Failed to fetch CSRF token for post-creation actions.")
                    csrf_ready = False

            if custom_display_name_enabled and csrf_ready:
                payload = {
                    "userId": user_id,
                    "newDisplayName": display_name,
                    "showAgedUpDisplayName": False
                }
                response = session.patch(url=f"https://users.roblox.com/v1/users/{user_id}/display-names", headers=headers6(csrf_token, "users.roblox.com"), json=payload, timeout=15)
                if response.status_code == 200:
                    set_display_name = True
                else:
                    wprint(f"Display name change failed with status code {response.status_code}: {response.text}")

            if ev_enabled and csrf_ready:
                email, reason = get_email(session)
                if email:
                    payload = {
                        "emailAddress": email,
                        "password": ""
                    }
                    response = session.post(url="https://accountsettings.roblox.com/v1/email", headers=headers6(csrf_token, "accountsettings.roblox.com"), json=payload, timeout=15)
                    if response.status_code == 200:
                        ticket, reason = get_inbox(session, email)
                        if ticket:
                            payload = {"ticket": ticket}
                            response = session.post(url="https://accountinformation.roblox.com/v1/email/verify", headers=headers6(csrf_token, "accountinformation.roblox.com"), json=payload, timeout=15)
                            if "verifiedUserHatAssetId" in response.text:
                                verified = True
                            else:
                                wprint(f"Email verify failed with status code {response.status_code}: {response.url}")
                        else:
                            wprint(f"Failed to fetch inbox content: {reason}")
                    else:
                        wprint(f"Email verify failed with status code {response.status_code}: {response.url}")
                else:
                    wprint(f"Failed to fetch temp email from API: {reason}")

            with lock:
                os.makedirs("output", exist_ok=True)
                if verified and custom_display_name_enabled and set_display_name:
                    with open("output/verified_accounts.txt", "a", encoding="utf-8") as file:
                        file.write(f"{user_id}:{username}:{email}:{password}:{cookie}\n")
                    msg = f"Account created & email verified: @{username} ({display_name})"
                elif verified:
                    with open("output/verified_accounts.txt", "a", encoding="utf-8") as file:
                        file.write(f"{user_id}:{username}:{email}:{password}:{cookie}\n")
                    msg = f"Account created & email verified: @{username}"
                elif custom_display_name_enabled and set_display_name:
                    with open("output/accounts.txt", "a", encoding="utf-8") as file:
                        file.write(f"{user_id}:{username}:{password}:{cookie}\n")
                    msg = f"Account created: @{username} ({display_name})"
                else:
                    with open("output/accounts.txt", "a", encoding="utf-8") as file:
                        file.write(f"{user_id}:{username}:{password}:{cookie}\n")
                    msg = f"Account created: @{username}"
            crprint(msg)
            update_counter("generated")
            continue
            
        except Exception as e:
            error_msg = str(e).lower()
            if "could not resolve proxy" in error_msg:
                fprint(f"Failed to send request (5). The proxy might be invalid or unreachable. Proxy: {proxy}")
            elif "timed out" in error_msg:
                fprint(f"Request timed out (28). Proxy: {proxy}")
            elif "unsupported proxy syntax" in error_msg:
                fprint(f"Wrong proxy format (5). Please use the following format: 'username:password@host:port'. Proxy: {proxy}")
            elif "failed to connect to" in error_msg:
                fprint(f"Connection failed (7): Could not connect to server. Proxy: {proxy}")
            elif "proxy connect aborted" in error_msg:
                fprint(f"Proxy CONNECT aborted. (56) The proxy may have refused the connection. Proxy: {proxy}")
            elif "connect tunnel failed" in error_msg:
                fprint(f"CONNECT tunnel failed (7). The proxy might be blocking the connection. Proxy: {proxy}")
            elif "ssl certificate problem" in error_msg:
                    fprint(f"SSL certificate problem. (60) The server certificate is invalid or untrusted. Proxy: {proxy}")
            elif "failed to perform, curl: (16)" in error_msg:
                fprint(f"HTTP/2 framing error (16). The proxy or server has HTTP/2 protocol issues. Proxy: {proxy}")
            elif "failed to perform, curl: (35)" in error_msg:
                fprint(f"TLS/SSL connection failed (35). Likely OpenSSL or proxy issue. Proxy: {proxy}")
            else:
                fprint(f"Unexpected error: {e}")

            update_counter("failed")
            time.sleep(5)
            continue
