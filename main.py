import threading, os
from core import thread_worker
from utils import *
from tempmail import get_tempmail_public_apiKey

def main():
    global thread_restart_enabled
    
    set_console_title("Roblox Account Generator By: t.me/occursive")
    
    proxy_list = load_proxies("input/proxies.txt")
    if not proxy_list:
        fprint("Failed to load any proxies.")
        safe_exit()
        return
    
    config = load_config()
    email_verification = config.get("email_verification", False)
    
    if email_verification:
        safe_print(f"{f.LIGHTBLUE_EX}Email verification: {f.LIGHTGREEN_EX}enabled\n{s.RESET_ALL}")
        safe_print(f"{f.LIGHTBLUE_EX}Fetching tempmail API key...{s.RESET_ALL}")
        api_key, error = get_tempmail_public_apiKey()
        if not api_key:
            safe_print(f"{f.LIGHTRED_EX}Failed to fetch tempmail API key: {error}")
            safe_exit()
            return
        safe_print(f"{f.LIGHTGREEN_EX}Successfully fetched tempmail API key.\n{s.RESET_ALL}")
    else:
        safe_print(f"{f.LIGHTBLUE_EX}Email verification: {f.LIGHTRED_EX}disabled\n{s.RESET_ALL}")
    
    target_thread_count = input_thread_count()
    if target_thread_count is None:
        return
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    set_start_time()
    
    safe_print(f"{f.LIGHTGREEN_EX}🚀 Tool successfully started!{s.RESET_ALL}\n")
    
    for i in range(target_thread_count):
        start_worker_thread(i + 1, thread_worker)
    
    monitor_thread = threading.Thread(target=thread_monitor, args=(thread_worker,), daemon=True)
    monitor_thread.start()
    
    try:
        monitor_thread.join()
    except KeyboardInterrupt:
        thread_restart_enabled = False
        safe_exit()

if __name__ == "__main__":
    main()
