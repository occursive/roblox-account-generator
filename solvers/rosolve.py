
import requests, json, time

API_BASE = "https://rosolve.pro"
max_attempts = 30

def rs_get_token(blob, proxy, api_key, timeout=30):
    challengeInfo = {
        'publicKey': 'A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F',
        'site': 'https://www.roblox.com',
        'surl': 'https://arkoselabs.roblox.com',
        'capiMode': 'inline',
        'styleTheme': 'default',
        'languageEnabled': False,
        'jsfEnabled': False,
        'extraData': {'blob': blob},
        'ancestorOrigins': ['https://www.roblox.com'],
        'treeIndex': [0],
        'treeStructure': '[[]]',
        'locationHref': 'https://www.roblox.com/arkose/iframe',
        'documentReferrer': 'https://www.roblox.com/',
        'storageAccess': False,
        'cookieTimestamp': False,
        'solvePOW': True
    }
    
    browserInfo = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache': True,
        'Sec-Ch-Ua': '\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mobile': False
    }
    
    payload = {
        'key': api_key,
        'challengeInfo': challengeInfo,
        'browserInfo': browserInfo,
        'proxy': f"http://{proxy}"
    }
    
    proxies = {
        "http": f"http://{proxy}", 
        "https": f"http://{proxy}"
    }
    
    try:
        response = requests.post(f'{API_BASE}/createTask', json=payload, timeout=timeout, proxies=proxies)
        if response.status_code == 522:
            return None, "Rosolve's service is temporarily unavailable. Please try again later."
        
        if response.status_code == 523:
            return None, "Rosolve's service is currently unreachable. Please try again later."
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                message = error_data.get("error", "Unknown error")
                return None, f"HTTP {response.status_code}: {message}"
            except json.JSONDecodeError:
                return None, f"HTTP {response.status_code}: {response.text[:100]}"
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return None, f"Invalid JSON response: {response.text[:100]}"
        
        task_id = response_data.get('taskId')
        
        if not task_id:
            error_msg = response_data.get('error', 'Unknown error')
            if 'api key' in error_msg.lower() or 'invalid key' in error_msg.lower():
                return None, "Invalid Rosolve API key! Please check your API key."
            return None, f"Failed to get taskId, reason: {error_msg}"

    except requests.exceptions.RequestException as e:
        return None, f"Network error during task creation: {str(e)}"
    except Exception as e:
        return None, f"Failed to solve captcha! Code: 04 | {e}"

    for attempt in range(max_attempts):
        try:
            solution_response = requests.get(f'{API_BASE}/taskResult/{task_id}', timeout=timeout)
            
            if solution_response.status_code != 200:
                if solution_response.status_code == 522:
                    return None, "Captcha solver temporarily unreachable. Please try again later."
                if solution_response.status_code == 500:
                    try:
                        solution = solution_response.json()
                        error_msg = solution.get('result', {}).get('error', 'Unknown error')
                        if 'Failed to solve the captcha' in error_msg:
                            return None, "Failed to solve captcha: Service was unable to solve it."
                        return None, error_msg
                    except:
                        pass
                return None, f"Status check failed: HTTP {solution_response.status_code}"
            
            try:
                solution = solution_response.json()
            except json.JSONDecodeError:
                return None, f"Invalid JSON in status response: {solution_response.text[:100]}"
            
        except requests.exceptions.RequestException as e:
            return None, f"Network error during status check: {str(e)}"
        except Exception as e:
            return None, f"Code: 02 | Reason: {e}"
        
        status = solution.get('status')
        
        if status == 'failed':
            return None, "Server returned failed status."
        
        if status == 'completed':
            result = solution.get('result')
            if isinstance(result, dict) and 'solution' in result:
                token = result['solution']
                return token, None
            else:
                return None, f"Captcha completed but invalid result format: {result}"
        
        time.sleep(1)
    
    return None, f"Captcha solving did not complete in time. Timed out after {max_attempts} attempts."
