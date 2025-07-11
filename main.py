import time, os, ctypes, threading
from utils import wprint
from core import start

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

generated = 0
failed = 0
crashed = False

lock = threading.Lock()
start_time = None

def worker():
    global generated, failed, crashed
    while not crashed:
        success, local_crashed = start()
        with lock:
            if local_crashed:
                crashed = True
            elif success:
                generated += 1
            else:
                failed += 1

def title_updater():
    while not crashed:
        with lock:
            if start_time is None:
                continue
            elapsed = time.time() - start_time
            minutes = elapsed / 60 if elapsed > 0 else 1
            cpm = generated / minutes
            hours, rem = divmod(elapsed, 3600)
            minutes_elapsed, seconds = divmod(rem, 60)
            time_str = f"{int(hours):02}:{int(minutes_elapsed):02}:{int(seconds):02}"
            set_console_title(f"Roblox Account Generator By: t.me/occursive | Generated: {generated} | Failed: {failed} | CPM: {cpm:.2f} | Runtime: {time_str}")
        time.sleep(1)

if __name__ == "__main__":
    set_console_title("Roblox Account Generator By: t.me/occursive")

    while True:
        thread_count = input(" > Enter number of threads (1-10): ")
        if thread_count.isdigit():
            thread_count = int(thread_count)
            if 1 <= thread_count <= 10:
                os.system('cls')
                break
            else:
                wprint("Please enter a number between 1 and 10.")
        else:
            wprint("Invalid input. Only numbers are allowed.")

    start_time = time.time()

    threads = []
    updater_thread = threading.Thread(target=title_updater, daemon=True)
    updater_thread.start()

    for _ in range(thread_count):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
