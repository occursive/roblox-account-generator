from time import sleep

API_BASE = "https://rosolve.pro"
max_attempts = 30

def rs_get_token(session, blob, proxy, api_key, timeout=30):
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
    
    try:
        response = session.post(f'{API_BASE}/createTask', json=payload, timeout=timeout)
        if response.status_code == 522:
            return None, "Rosolve's service is temporarily unavailable. Please try again later."
        
        if response.status_code == 523:
            return None, "Rosolve's service is currently unreachable. Please try again later."
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                message = error_data.get("error", "Unknown error")
                return None, f"HTTP {response.status_code}: {message}"
            except Exception:
                return None, f"HTTP {response.status_code}: {response.text[:100]}"
        
        try:
            response_data = response.json()
        except Exception as ve:
            return None, f"Invalid JSON from solver (createTask): {ve}"
        
        task_id = response_data.get('taskId')
        
        if not task_id:
            error_msg = response_data.get('error', 'Unknown error')
            if 'api key' in error_msg.lower() or 'invalid key' in error_msg.lower():
                return None, "Invalid Rosolve API key! Please check your API key."
            return None, f"Failed to get taskId, reason: {error_msg}"

    except Exception as e:
        return None, f"Network error during task creation: {e}"

    for attempt in range(max_attempts):
        try:
            payload = {
                "key": api_key,
                "taskId": task_id
            }
            
            solution_response = session.post(f'{API_BASE}/taskResult', json=payload, timeout=timeout)
            
            if solution_response.status_code != 200:
                if solution_response.status_code == 522:
                    return None, "Captcha solver temporarily unreachable. Please try again later."
                if solution_response.status_code == 500:
                    try:
                        solution_tmp = solution_response.json()
                        error_msg = (solution_tmp.get('result') or {}).get('error') or solution_tmp.get('error') or 'Unknown error'
                        if 'Failed to solve the captcha' in error_msg:
                            return None, "Service was unable to solve it."
                        return None, error_msg
                    except Exception:
                        pass
                try:
                    err = solution_response.json()
                    err_msg = err.get('error') or (err.get('result') or {}).get('error') or 'Unknown error'
                except Exception:
                    err_msg = solution_response.text[:100]
                return None, f"Status check failed: HTTP {solution_response.status_code}: {err_msg}"
            
            try:
                solution = solution_response.json()
            except Exception as ve:
                return None, f"Invalid JSON from solver (taskResult): {ve}"
            
        except Exception as e:
            return None, f"Network error during status check: {e}"
        
        status = solution.get('status')
        
        if status == 'failed':
            err_msg = (solution.get('result') or {}).get('error') or solution.get('error') or "Server returned failed status."
            return None, err_msg
        
        if status == 'completed':
            result = solution.get('result')
            token = None
            if isinstance(result, dict):
                token = result.get('solution') or result.get('token')
            elif isinstance(result, str):
                token = result
            if token:
                return token, None
            return None, f"Captcha completed but invalid result format: {result}"
        sleep(1)
    return None, f"Captcha solving did not complete in time. Timed out after {max_attempts} attempts."
