import requests, re, time, urllib
from threading import Lock

tempmail_public_apiKey = None
tempmail_lock = Lock()

def get_tempmail_public_apiKey():
    global tempmail_public_apiKey
    with tempmail_lock:
        if tempmail_public_apiKey:
            return tempmail_public_apiKey, None
    try:
        response = requests.get("https://v3.priyo.email/api-docs", timeout=10)
        match = re.search(r'<input.*?type=["\']password["\'].*?value=["\']([^"\']+)["\']', response.text, re.IGNORECASE | re.DOTALL)
        if match:
            with tempmail_lock:
                tempmail_public_apiKey = match.group(1)
            return tempmail_public_apiKey, None
        else:
            return None, "API key not found in response"
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except requests.exceptions.ConnectionError:
        return None, "Connection error - unable to reach the site"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def get_email(session):
    retry_count = 0
    max_retries = 2
    
    while retry_count <= max_retries:
        try:
            response = session.get(f"https://free.priyo.email/api/random-email/{tempmail_public_apiKey}", timeout=15)
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError as ve:
                    return None, f"Invalid JSON response ({ve})"
                if isinstance(data, dict):
                    email = data.get("email")
                    if email:
                        return email, None
                    else:
                        return None, "'email' key not found in JSON response"
                else:
                    return None, "JSON response is not a dict (invalid email format)"
            else:
                return None, f"Status code {response.status_code}"
        except Exception as e:
            retry_count += 1
            if retry_count > max_retries:
                if "could not resolve proxy" in str(e).lower():
                    return None, "Proxy might be invalid or unreachable."
                elif "timed out" in str(e).lower():
                    return None, "Timed out."
                else:
                    return None, f"{e}"
            time.sleep(1)

def get_inbox(session, email):
    error_retry_count = 0
    max_error_retries = 3
    empty_data_count = 0
    max_empty_data_retries = 15
    
    while True:
        try:
            response = session.get(f"https://free.priyo.email/api/messages/{email}/{tempmail_public_apiKey}", timeout=10)
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError as ve:
                return None, f"Invalid JSON response ({ve})"
            if not data:
                empty_data_count += 1
                if empty_data_count > max_empty_data_retries:
                    return None, "No messages received after maximum retries."
                time.sleep(1)
                continue
            try:
                html_content = data[0].get("content", "")
                match = re.search(r'<a[^>]*class=["\'][^"\']*email-button[^"\']*["\'][^>]*href=["\'][^"\']*ticket=([^"&\']+)', html_content, re.IGNORECASE | re.DOTALL)
                if match:
                    ticket = match.group(1)
                    ticket_decoded = urllib.parse.unquote(ticket)
                    return ticket_decoded, None
                else:
                    empty_data_count += 1
                    if empty_data_count > max_empty_data_retries:
                        return None, "Ticket not found in email content after maximum retries."
                    time.sleep(1)
                    continue
            except Exception as regex_error:
                return None, f"Inbox parsing failed: {regex_error}"
        except Exception as e:
            error_retry_count += 1
            if error_retry_count > max_error_retries:
                if "could not resolve proxy" in str(e).lower():
                    return None, "Proxy might be invalid or unreachable."
                elif "timed out" in str(e).lower():
                    return None, "Timed out."
                else:
                    return None, f"{e}"
            time.sleep(1)
