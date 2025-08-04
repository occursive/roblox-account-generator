from core import thread_worker
from utils import *
import threading
import os

def main():
    global thread_restart_enabled
    
    set_console_title("Roblox Account Generator By: t.me/occursive")
    
    proxy_list = load_proxies("input/proxies.txt")
    if not proxy_list:
        fprint("Failed to load any proxies.")
        safe_exit()
        return
    
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
