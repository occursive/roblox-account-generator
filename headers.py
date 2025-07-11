def header1(csrf_token):
    return {
    "host": "auth.roblox.com",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-csrf-token": csrf_token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "origin": "https://www.roblox.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.roblox.com/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9"
}
    
def header2(csrf_token):
    return {
    "host": "auth.roblox.com",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-csrf-token": csrf_token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "origin": "https://www.roblox.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.roblox.com/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
}
    
def header3(csrf_token):
    return {
    "host": "apis.roblox.com",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-csrf-token": csrf_token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "origin": "https://www.roblox.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.roblox.com/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
}
     
def header4(encrypted_challenge_metadata, csrf_token, challenge_id):
    return {
    "host": "auth.roblox.com",
    "rblx-challenge-metadata": encrypted_challenge_metadata,
    "sec-ch-ua-platform": "\"Windows\"",
    "x-csrf-token": csrf_token,
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "rblx-challenge-id": challenge_id,
    "rblx-challenge-type": "captcha",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "x-retry-attempt": "1",
    "origin": "https://www.roblox.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.roblox.com/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
}