import threading, os
from core import thread_worker, set_runtime_options
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
    acc_settings = config.get("account_settings", {})
    ev_raw = acc_settings.get("email_verification", False)
    if isinstance(ev_raw, dict):
        email_verification = ev_raw.get("enabled", False)
    else:
        email_verification = bool(ev_raw)
    
    dn_cfg = acc_settings.get("display_name", {})
    dn_enabled = dn_cfg.get("enabled", False) if isinstance(dn_cfg, dict) else False
    dn_mode = dn_cfg.get("mode", "custom") if isinstance(dn_cfg, dict) else "custom"
    dn_custom_name = dn_cfg.get("custom_name", "") if isinstance(dn_cfg, dict) else ""

    cp_cfg = acc_settings.get("custom_password", {})
    cp_enabled = cp_cfg.get("enabled", False) if isinstance(cp_cfg, dict) else False
    cp_password = cp_cfg.get("password", "") if isinstance(cp_cfg, dict) else ""

    safe_print(f"{f.LIGHTBLUE_EX}Settings:")
    if cp_enabled:
        safe_print(f"{f.LIGHTBLUE_EX} ├─ Custom password: {f.LIGHTGREEN_EX}enabled{f.WHITE}/{f.LIGHTBLACK_EX}disabled {f.LIGHTBLACK_EX}({cp_password})\n{f.LIGHTBLUE_EX} │")
    else:
        safe_print(f"{f.LIGHTBLUE_EX} ├─ Custom password: {f.LIGHTBLACK_EX}enabled{f.WHITE}/{f.LIGHTRED_EX}disabled\n{f.LIGHTBLUE_EX} │")

    if email_verification:
        safe_print(f"{f.LIGHTBLUE_EX} ├─ Email verification: {f.LIGHTGREEN_EX}enabled{f.WHITE}/{f.LIGHTBLACK_EX}disabled\n{f.LIGHTBLUE_EX} │")
    else:
        safe_print(f"{f.LIGHTBLUE_EX} ├─ Email verification: {f.LIGHTBLACK_EX}enabled{f.WHITE}/{f.LIGHTRED_EX}disabled\n{f.LIGHTBLUE_EX} │")

    if dn_enabled:
        safe_print(f"{f.LIGHTBLUE_EX} └─ Custom display name: {f.LIGHTGREEN_EX}enabled{f.WHITE}/{f.LIGHTBLACK_EX}disabled")
        if dn_mode == "custom":
            safe_print(f" {f.LIGHTBLUE_EX}    └─ Mode: {f.LIGHTBLACK_EX}{dn_mode} ({f.LIGHTBLACK_EX}{dn_custom_name})\n")
        else:
            safe_print(f" {f.LIGHTBLUE_EX}    └─ Mode: {f.LIGHTBLACK_EX}{dn_mode}\n")
    else:
        safe_print(f"{f.LIGHTBLUE_EX} └─ Custom display name: {f.LIGHTBLACK_EX}enabled{f.WHITE}/{f.LIGHTRED_EX}disabled\n")

    if email_verification:
        safe_print(f"{f.LIGHTBLUE_EX}Fetching tempmail API key..")
        api_key, error = get_tempmail_public_apiKey()
        if not api_key:
            safe_print(f" {f.LIGHTBLUE_EX}└─{f.LIGHTRED_EX} Failed to fetch tempmail API key: {error}")
            safe_exit()
            return
        safe_print(f" {f.LIGHTBLUE_EX}└─{f.LIGHTGREEN_EX} Successfully fetched tempmail API key.\n")

    set_runtime_options(email_verification, dn_cfg if isinstance(dn_cfg, dict) else {})
    set_runtime_custom_password(cp_cfg if isinstance(cp_cfg, dict) else {})
    
    target_thread_count = input_thread_count()
    if target_thread_count is None:
        return
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    set_start_time()
    
    safe_print(f"{f.LIGHTGREEN_EX}🚀 Tool successfully started!\n")
    
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
