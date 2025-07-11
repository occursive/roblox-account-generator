from time import sleep
import requests


API_BASE = "http://fastcap.xyz/api"
max_attempts = 10

def get_token(blob, proxy, fastcap_apiKey):
    if not fastcap_apiKey:
        return True, True, None, "Invalid Fastcap API key! The 'fastcap_apiKey' value in 'input/config.json' is empty or missing. Please update it."
    body = {
        "api_key": fastcap_apiKey,
        "site_key": "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F",
        "blob": blob,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "do_all_requests": True,
        "proxy": proxy
    }

    try:
        response = requests.post(f"{API_BASE}/createTask", json=body)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            if status == "PROCESSING":
                response.raise_for_status()
                task_id = response.json().get("task_id")
                if not task_id:
                    return True, False, None, "Failed to solve captcha! The API did not return a task ID."
            else:
                return True, False, None, f"Failed to solve captcha! Reason: {response.text}"
        else:
            data = response.json()
            status = data.get("status")
            if status == 400 or status == "400":
                message = data.get("message")
                if message == "Invalid API key":
                    return True, True, None, "Invalid Fastcap API key! Please update it in 'input/config.json'."
                else:
                    return True, True, None, f"Failed to solve captcha! Reason: {message}"
    except Exception as e:
        return True, True, None, f"Failed to solve captcha! Code: 04 | {e}"

    for _ in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE}/getTask/{task_id}")
            data = response.json()
        except Exception as e:
            return True, True, None, f"Failed to solve captcha! Code: 02 Reason: {e}"
        status = data.get("status")
        if status == "FAILED":
            return True, False, None, "Failed to solve captcha! Server returned FAILED status."
        if status == "DONE":
            return False, False, data.get("result", {}).get("token"), None
        sleep(3)
    return True, False, None, f"Captcha solving did not complete in time. Timed out after {max_attempts} attempts."
