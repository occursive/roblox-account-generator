from time import sleep
import requests
import json


API_BASE = "http://fastcap.xyz/api"
max_attempts = 10

def fc_get_token(blob, proxy, api_key):
    body = {
        "api_key": api_key,
        "site_key": "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F",
        "blob": blob,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "do_all_requests": True,
        "proxy": f"http://{proxy}"
    }

    proxies = {
        "http": f"http://{proxy}", 
        "https": f"http://{proxy}"
    }
    
    try:
        response = requests.post(f"{API_BASE}/createTask", json=body, timeout=120, proxies=proxies)
        
        if response.status_code == 523:
            return None, "Fastcap.xyz server is unreachable (HTTP 523 - Cloudflare error). Service may be down."
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                message = error_data.get("message", "Unknown error")
                return None, f"HTTP {response.status_code}: {message}"
            except json.JSONDecodeError:
                return None, f"HTTP {response.status_code}: {response.text[:100]}"
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            return None, f"Invalid JSON response: {response.text[:100]}"
        
        status = data.get("status")
        
        if status == "PROCESSING":
            task_id = data.get("task_id")
            if not task_id:
                return None, "The API did not return a task ID."
        elif status == "400" or status == 400:
            message = data.get("message")
            if message == "Invalid API key":
                return None, "Invalid Fastcap API key! Please update it in 'input/config.json'."
            else:
                return None, f"Reason: {message}"
        else:
            return None, f"Unexpected status: {status}"

    except requests.exceptions.RequestException as e:
        return None, f"Network error during task creation: {str(e)}"
    except Exception as e:
        return None, f"Code: 04 | {e}"

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE}/getTask/{task_id}", timeout=30)
            
            if response.status_code != 200:
                return None, f"Status check failed: HTTP {response.status_code}"
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                return None, f"Invalid JSON in status response: {response.text[:100]}"
            
        except requests.exceptions.RequestException as e:
            return None, f"Network error during status check: {str(e)}"
        except Exception as e:
            return None, f"Code: 02 Reason: {e}"
        
        status = data.get("status")
        text = data.get("error")

        if status == "FAILED":
            return None, f"Server returned FAILED status. Reason: {text}"
        
        if status == "DONE":
            token = data.get("result", {}).get("token")
            if token:
                return token, None
            else:
                return None, "Captcha completed but no token received."
        sleep(3)
    
    return None, f"Captcha solving did not complete in time. Timed out after {max_attempts} attempts."
