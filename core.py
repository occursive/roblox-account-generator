import base64, html, time, json, random, threading, os
from curl_cffi import requests
from headers import headers1, headers2, headers4, headers5
from utils import *
from solvers.fastcap import fc_get_token
from solvers.rosolve import rs_get_token
from secure_auth import get_sa

SOLVER, API_KEY = validate_solver_config()

SOLVER_FUNCTIONS = {
    "fastcap": fc_get_token,
    "rosolve": rs_get_token
}

MAX_CONSECUTIVE_CAPTCHA_FAILS = 30

consecutive_captcha_fails = 0
captcha_fail_lock = threading.Lock()

def thread_worker():
    global consecutive_captcha_fails, thread_restart_enabled
    while thread_restart_enabled:
        try:
            proxy_lines = load_proxies("input/proxies.txt")
            if not proxy_lines:
                fprint("No proxies available. Exiting...")
                break
            
            proxy = random.choice(proxy_lines)
            proxies = {
                "http": f"http://{proxy}", 
                "https": f"http://{proxy}"
            }

            session = requests.Session(
                impersonate="chrome", 
                proxies=proxies
            )

            response = session.get(url="https://www.roblox.com/", headers=headers1())

            if response.status_code == 429:
                fprint(f"API rate limit hit! {response.url}")
                update_counter("failed")
                time.sleep(10)
                continue
            if "data-token=" in response.text:
                raw_token = response.text.split('data-token="')[1].split('"')[0]
                csrf_token = html.unescape(raw_token)

            username = generate_username()
            birthday = generate_birthday()
            password = generate_password()

            payload = {
                "username": username,
                "context": "Signup",
                "birthday": birthday
            }

            response = session.post(url="https://auth.roblox.com/v1/usernames/validate", headers=headers2(csrf_token), json=payload)

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
                    username = generate_username()

                payload = {
                    "username": username,
                    "context": "Signup",
                    "birthday": birthday
                }

                response = session.post(url="https://auth.roblox.com/v1/usernames/validate", headers=headers2(csrf_token), json=payload)

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
            response = session.post(url="https://auth.roblox.com/v2/passwords/validate", headers=headers2(csrf_token), json=payload)
            data = response.json()

            if data["message"] != "Password is valid":
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

            response = session.post(url="https://auth.roblox.com/v2/signup", headers=headers4(csrf_token, "auth.roblox.com"), json=signup_payload)
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
            data, reason = solver_func(blob, proxy, API_KEY)

            if data == None:
                with captcha_fail_lock:
                    if consecutive_captcha_fails >= MAX_CONSECUTIVE_CAPTCHA_FAILS:
                        break
                    consecutive_captcha_fails += 1
                    fprint(f"Failed to solve captcha: {reason}")
                    update_counter("failed")
                    if consecutive_captcha_fails == MAX_CONSECUTIVE_CAPTCHA_FAILS:
                        fprint(f"Too many consecutive captcha failures ({consecutive_captcha_fails}). Stopping all threads.")
                        thread_restart_enabled = False
                        threading.Thread(target=lambda: (time.sleep(0.5), safe_exit())).start()
                continue
                
            with captcha_fail_lock:
                consecutive_captcha_fails = 0
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

            response = session.post(url="https://apis.roblox.com/challenge/v1/continue", headers=headers4(csrf_token, "apis.roblox.com"), json=payload)

            if response.status_code != 200:
                fprint(f"Request failed with status code {response.status_code}: {response.url}")
                update_counter("failed")
                continue

            encrypted_metadata = base64.b64encode(json.dumps(metadata).encode('utf-8')).decode('utf-8')

            response = session.post(url="https://auth.roblox.com/v2/signup", headers=headers5(encrypted_metadata, csrf_token, challenge_id), json=signup_payload)

            if response.status_code != 200:
                fprint(f"Request failed with status code {response.status_code}: {response.url}")
                update_counter("failed")
                continue
            
            data = response.json()
            user_id = data['userId']
            
            with lock:
                os.makedirs("output", exist_ok=True)
                with open("output/accounts.txt", "a", encoding="utf-8") as file:
                    file.write(f"{user_id}:{username}:{password}:{response.cookies['.ROBLOSECURITY']}\n")
                
            crprint(f"Account created: {username}")
            update_counter("generated")
            
        except Exception as e:
            if 'failed to do request:' in str(e):
                fprint(f"Failed to send request. The proxy might be invalid or unreachable. Proxy: {proxy}")
                update_counter("failed")
            else:
                fprint(f"Error: {e}")
            update_counter("failed")
            time.sleep(5)
            continue
