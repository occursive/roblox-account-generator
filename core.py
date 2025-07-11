from utils import sprint, caprint, crprint, wprint, fprint, get_proxy, generate_username, generate_birthday, generate_password
from headers import header1, header2, header3, header4
from json import load, loads
from threading import Lock
from secure_auth import get_sa
from solver import get_token
from colorama import init
import tls_client, json, base64, html
init(autoreset=True)
lock = Lock()

with open("input/config.json", "r", encoding="utf-8") as file:
    config = load(file)
    
proxy_type = config['proxy_type']
fastcap_apikey = config['fastcap_apiKey']

max_retries = 10
error_count = 0

def start():
    global error_count
    try:
        proxy = get_proxy(proxy_type)
        if proxy == None:
            return False, True
        session = tls_client.Session(
            client_identifier="firefox_102",
            random_tls_extension_order=True
        )
        
        response = session.get(url="https://www.roblox.com/", proxy=proxy)
        if response.status_code == 429:
            wprint(f"API rate limit hit! {response.url}")
            return False, False
        if 'data-token=' in response.text:
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

        response = session.post(url="https://auth.roblox.com/v1/usernames/validate", headers=header1(csrf_token) , json=payload, proxy=proxy)
        if response.status_code == 429:
            wprint(f"API rate limit hit! {response.url}")
            return False, False
        data = response.json()
        while data["message"] != "Username is valid":
            if data["message"] == "Username is already in use":
                wprint(f"Username is already in use: {username}")
            elif data["message"] == "Usernames can be 3 to 20 characters long":
                wprint(f"Usernames can be 3 to 20 characters long: {username}")
            username = generate_username()
            payload = {
                "username": username,
                "context": "Signup",
                "birthday": birthday
            }

            response = session.post(url="https://auth.roblox.com/v1/usernames/validate", headers=header1(csrf_token) , json=payload, proxy=proxy)
            if response.status_code == 429:
                wprint(f"API rate limit hit! {response.url}")
                return False, False
        sprint(f"Account generation started: {username}")
        client_public_key, client_epoch_timestamp, server_nonce, sai_signature = get_sa(proxy)
            
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

#https://t.me/occursive

        response = session.post(url="https://auth.roblox.com/v2/signup", headers=header2(csrf_token) , json=signup_payload, proxy=proxy)
        if response.status_code == 429:
            wprint(f"API rate limit hit! {response.url}")
            return False, False
        if response.status_code == 403:
            challenge_id = response.headers.get("Rblx-Challenge-Id")
            challenge_metadata = response.headers.get("Rblx-Challenge-Metadata")
            if challenge_id == None:
                fprint("Rblx-Challenge-Id header not found.")
                return False, False
            
        metadata = loads(base64.b64decode(challenge_metadata.encode("utf-8")).decode("utf-8"))
        blob = metadata.get("dataExchangeBlob")
        captcha_id = metadata.get("unifiedCaptchaId")

        error, crash, data, reason = get_token(blob, proxy, fastcap_apikey)
        if crash:
            fprint(reason)
            return False, True
        if error:
            fprint(reason)
            return False, False
        md = data.split("|")[0] + data.split("pk=A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F")[1].split("|cdn_url=")[0]
        caprint(f"Captcha solved: {md}")
        
        challenge_metadata2 = json.dumps({
            "unifiedCaptchaId": captcha_id,
            "captchaToken": data,
            "actionType": "Signup"
        }, separators=(',', ':'))
            
        payload = json.dumps({
            "challengeId": challenge_id,
            "challengeType": "captcha",
            "challengeMetadata": challenge_metadata2
        }, separators=(',', ':')) 
            
        response = session.post(url="https://apis.roblox.com/challenge/v1/continue", headers=header3(csrf_token) , json=payload, proxy=proxy)
        if response.status_code != 200:
            fprint(f"Failed to send request to: {response.url}")
            return False, False
        elif response.status_code == 200:
            encrypted_challenge_metadata = base64.b64encode(challenge_metadata2.encode('utf-8')).decode('utf-8')
            response = session.post(url="https://auth.roblox.com/v2/signup", headers=header4(encrypted_challenge_metadata, csrf_token, challenge_id) , json=signup_payload, proxy=proxy)

            if response.status_code != 200:
                fprint(f"Signup request failed! {response.text}")
                return False, False
            data = response.json()
            user_id = data['userId']
            with lock:
                with open("output/accounts.txt", "a", encoding="utf-8") as file:
                    file.write(f"{user_id}:{username}:{password}:{response.cookies['.ROBLOSECURITY']}\n")
            crprint(f"Account created: {username}")
            return True, False

    except Exception as e:
        if 'failed to do request:' in str(e):
            error_count += 1
            retries_left = max_retries - error_count
            fprint(f"Failed to send request. The proxy might be invalid or unreachable. Retries left: {retries_left}")
            if retries_left == 0:
                fprint("No retries left. Please check the proxy settings in 'input/config.json' or the proxy list in 'input/proxies.txt'.")
                return False, True
            return False, False
        else:
            fprint(f"{e}")
        return False, True