import random, string, os, sys, json, time, threading
from datetime import datetime
from colorama import Fore as f, Style as s, init
from threading import Lock

init(autoreset=False)

lock = Lock()
threads_lock = Lock()
print_lock = Lock()

generated_count = 0
failed_count = 0
start_time = None

target_thread_count = 0
thread_restart_enabled = True
threads_list = []
thread_counter = 0

CUSTOM_PASSWORD_CFG_RUNTIME = {}

def set_runtime_custom_password(cfg):
    global CUSTOM_PASSWORD_CFG_RUNTIME
    CUSTOM_PASSWORD_CFG_RUNTIME = cfg if isinstance(cfg, dict) else {}

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def color_print(label, label_color, text_color, text):
    with lock:
        print(f"{label_color}[{label}]{f.WHITE} - {f.LIGHTBLACK_EX}{get_time()} » {text_color}{text}{s.RESET_ALL}")
def sprint(text):
    color_print("STARTED", f.CYAN, f.LIGHTCYAN_EX, text)
def caprint(text):
    color_print("CAPTCHA", f.MAGENTA, f.LIGHTMAGENTA_EX, text)
def crprint(text):
    color_print("CREATED", f.GREEN, f.LIGHTGREEN_EX, text)
def wprint(text):
    color_print("WARNING", f.YELLOW, f.LIGHTYELLOW_EX, text)
def fprint(text):
    color_print("FAILURE", f.RED, f.LIGHTRED_EX, text)
def tprint(text):
    color_print("THREADS", f.MAGENTA, f.LIGHTMAGENTA_EX, text)

def generate_username():
    roots = ["zarn", "milo", "trev", "kayn", "luro", "jex", "naro", "vask", "dren", "xilo",
            "rilo", "synd", "quav", "bray", "tarn", "zayv", "lom", "fayr", "keld", "rix",
            "tharn", "vynz", "calo", "dran", "zelv", "fray", "nyro", "bex", "krev", "jorn",
            "sarn", "vex", "kryn", "drax", "lyn", "zor", "velk", "garo", "phin", "trex",
            "valk", "kael", "rius", "zeph", "noct", "aero", "viro", "arv", "kaid", "jor",
            "quin", "raen", "xen", "ziv", "torv", "rusk", "fenn", "kael", "tavi", "rusk",
            "sol", "kaos", "vyr", "zeno", "kade", "jexi", "nex", "aeth", "thane", "kaiv",
            "orik", "ravn", "skye", "thor", "ivar", "zeke", "zael", "dane", "mira", "lyra",
            "nyx", "kairo", "aldr", "dorian", "voss", "noxx", "ryke", "tovin", "fyr", "krix"]
    mods = ["flux", "dyn", "vyn", "stral", "grim", "lok", "vorn", "pran", "kaze", "thal",
            "myrk", "jinn", "zern", "cray", "vohl", "drux", "blen", "snok", "quen", "vrak",
            "zelk", "fryn", "nox", "brak", "skel", "throx", "drax", "vok", "kran", "morn",
            "shade", "volt", "nova", "rift", "blade", "quake", "storm", "ember", "flare", "frost",
            "bane", "hex", "lynx", "onyx", "pyre", "scorn", "venm", "wraith", "zeal", "geist",
            "drift", "gale", "void", "glint", "grimr", "haze", "spyr", "thorn", "quake", "wyrm"]
    ends = ["", "", "", str(random.randint(10, 99)), str(random.randint(100, 999)), str(random.randint(2005, 2024)),
            "ix", "or", "en", "um", "ax", "ul", "ev", "ar", "us", "et",
            "ion", "eus", "ius", "ean", "iel", "iel", "yx", "yx", "or", "is",
            "jr", "sr", "the", "neo", "arc", "kai", "zan", "rex", "lyn", "raz",
            "xv", "xii", "ix", "iv"]

    base = random.choice(roots).capitalize() + random.choice(mods)
    username = base
    if random.random() < 0.5:
        username += random.choice(ends)
    for a, b in [("a","4"), ("i","1"), ("o","0"), ("e","3")]:
        if random.random() < 0.25:
            username = username.replace(a, b)
    if len(username) < 15:
        username += str(random.randint(100,999))
    return username[:20], base

def generate_birthday():
    return f"{random.randint(1990,2004)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}T22:00:00.000Z"

def generate_password():
    required = [random.choice(string.ascii_uppercase),
                random.choice(string.ascii_lowercase),
                random.choice(string.digits), '$']
    remaining = random.choices(string.ascii_letters + string.digits + '$', k=12)
    password = required + remaining
    random.shuffle(password)
    return ''.join(password)

def get_password():
    custom_password = CUSTOM_PASSWORD_CFG_RUNTIME if isinstance(CUSTOM_PASSWORD_CFG_RUNTIME, dict) else {}
    if custom_password.get("enabled", False):
        return custom_password.get("password")
    return generate_password()

def load_proxies(filename):
    if not os.path.exists(filename):
        print(f"{f.YELLOW}Proxy file '{filename}' not found. Creating it...{s.RESET_ALL}")
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as file:
                file.write("username:password@host:port\n")
            print(f"{f.GREEN}Created '{filename}' with example format.{s.RESET_ALL}")
            fprint("Please add at least one proxy in the following format: 'username:password@host:port'.")
            return []
        except Exception as e:
            fprint(f"Error creating proxy file: {e}")
            return []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            proxies = [line.strip() for line in file if line.strip()]
    except Exception as e:
        fprint(f"Error reading proxies file: {e}")
        return []

    if len(proxies) == 1 and proxies[0] == "username:password@host:port":
        fprint(f"Proxy list contains only the example format. (File location: '{filename}')")
        fprint("Please add your actual proxies to the file.")
        return []

    if not proxies:
        fprint(f"Proxy list is empty. (File location: '{filename}')")
        fprint("Please add at least one proxy in the following format: 'username:password@host:port'.")
        return []

    validated_proxies = []
    needs_rewrite = False
    
    for proxy in proxies:
        if proxy.startswith(("https://", "socks4://", "socks5://")):
            protocol = proxy.split("://")[0]
            fprint(f"Error: Proxy protocol '{protocol}' is not supported. Currently only HTTP is supported.")
            fprint(f"Invalid proxy: {proxy}")
            continue

        if proxy.startswith("http://"):
            proxy = proxy[7:]
            needs_rewrite = True
        
        validated_proxies.append(proxy)
    
    if not validated_proxies:
        fprint("No valid proxies found after validation.")
        return []
    
    if needs_rewrite:
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for proxy in validated_proxies:
                    file.write(proxy + "\n")
            wprint("Removed http:// prefixes from proxies.txt and saved changes.")
        except Exception as e:
            fprint(f"Error updating proxy file: {e}.")

    return validated_proxies

def load_config():
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            
            proxy_type = config.get("proxy_type", "").lower()
            if proxy_type != "http":
                fprint(f"Error: Invalid proxy_type '{proxy_type}' in config.json.")
                fprint("Currently only 'http' is supported.")
                safe_exit()
            
            account_settings = config.get("account_settings", {})
            email_verification_cfg = account_settings.get("email_verification", None)
            if isinstance(email_verification_cfg, bool) or email_verification_cfg is None:
                pass
            elif isinstance(email_verification_cfg, dict):
                enabled = email_verification_cfg.get("enabled", False)
                if not isinstance(enabled, bool):
                    fprint("Error: account_settings.email_verification.enabled must be true/false in config.json.")
                    safe_exit()
            else:
                fprint("Error: account_settings.email_verification must be a boolean or an object in config.json.")
                safe_exit()

            display_cfg = account_settings.get("display_name", {})
            if display_cfg:
                if not isinstance(display_cfg, dict):
                    fprint("Error: account_settings.display_name must be an object in config.json.")
                    safe_exit()
                dn_enabled = display_cfg.get("enabled", False)
                if not isinstance(dn_enabled, bool):
                    fprint("Error: account_settings.display_name.enabled must be true/false in config.json.")
                    safe_exit()
                mode = display_cfg.get("mode", "custom")
                if mode not in ("custom", "from_username"):
                    fprint("Error: account_settings.display_name.mode must be 'custom' or 'from_username'.")
                    safe_exit()
                if dn_enabled and mode == "custom":
                    custom_name = display_cfg.get("custom_name", "")
                    if not isinstance(custom_name, str):
                        fprint("Error: account_settings.display_name.custom_name must be a string.")
                        safe_exit()
                    if not custom_name.strip():
                        fprint("Error: account_settings.display_name.custom_name cannot be empty when mode is 'custom'.")
                        safe_exit()
                    name_len = len(custom_name.strip())
                    if name_len < 3 or name_len > 20:
                        fprint("Error: account_settings.display_name.custom_name must be between 3 and 20 characters.")
                        safe_exit()
            
            account_settings = config.get("account_settings", {})
            custom_password = account_settings.get("custom_password", {})
            if custom_password.get("enabled", False):
                password = custom_password.get("password", "")
                if not password:
                    fprint("Error: account_settings.custom_password.password cannot be empty when custom_password.enabled is true.")
                    safe_exit()
                if len(password) < 8:
                    fprint(f"Error: account_settings.custom_password.password must be at least 8 characters (current: {len(password)}).")
                    safe_exit()
                if len(password) > 200:
                    fprint(f"Error: account_settings.custom_password.password must be at most 200 characters (current: {len(password)}).")
                    safe_exit()
                
            return config
    except FileNotFoundError:
        fprint("Config file not found: config.json.")
        safe_exit()
    except json.JSONDecodeError:
        fprint("Invalid JSON in config.json.")
        safe_exit()
    except Exception as e:
        fprint(f"Error loading config: {e}.")
        safe_exit()

def validate_solver_config():
    config = load_config()
    valid_solvers = ["rosolve"]
    
    captcha_settings = config.get("captcha_settings", {})
    if not captcha_settings:
        fprint("Error: captcha_settings is missing in config.json.")
        safe_exit()
    
    selected_solver = captcha_settings.get("selected_solver", "")
    
    if not selected_solver:
        fprint("Error: captcha_settings.selected_solver cannot be empty in config.json.")
        fprint(f"Valid options are: {', '.join(valid_solvers)}.")
        safe_exit()
    
    if selected_solver not in valid_solvers:
        fprint(f"Error: Invalid solver '{selected_solver}' in config.json.")
        fprint(f"Valid options are: {', '.join(valid_solvers)}.")
        safe_exit()
    
    api_keys = captcha_settings.get("api_keys", {})
    api_key = api_keys.get(selected_solver, "")
    
    if not api_key:
        fprint(f"Error: captcha_settings.api_keys.{selected_solver} cannot be empty in config.json.")
        fprint(f"Please add your {selected_solver} API key to captcha_settings.api_keys.{selected_solver} in config.json.")
        safe_exit()
    
    timeout = captcha_settings.get("timeout", 30)
    
    if not isinstance(timeout, (int, float)):
        fprint("Error: timeout value must be a number in config.json.")
        safe_exit()
    
    if timeout < 10 or timeout > 120:
        fprint(f"Error: timeout must be between 10 and 120 seconds (current: {timeout}).")
        safe_exit()
    
    return selected_solver, api_key, timeout

def set_console_title(title):
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except:
            pass
    elif os.name == "posix":
        try:
            sys.stdout.write(f"\x1b]0;{title}\x07")
            sys.stdout.flush()
        except:
            pass

def safe_exit():
    try:
        input(f"\n{f.LIGHTMAGENTA_EX}Press Enter to exit...{s.RESET_ALL}")
    except (EOFError, ValueError, KeyboardInterrupt):
        time.sleep(10)
    sys.exit(1)

def wait_for_threads_and_exit(message="All threads have stopped. Exiting..."):
    while get_active_worker_threads() > 0:
        time.sleep(0.5)
    
    tprint(message)
    safe_exit()

def set_start_time():
    global start_time
    start_time = time.time()

def get_runtime():
    if start_time is None:
        return "00:00:00"
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_active_worker_threads():
    with threads_lock:
        return sum(1 for t in threads_list if t.is_alive())

def update_title():
    if start_time is None:
        return
    elapsed = time.time() - start_time
    cpm = int((generated_count / elapsed) * 60) if elapsed > 0 else 0
    active_threads = get_active_worker_threads()
    title = f"Roblox Account Generator By: t.me/occursive | Runtime: {get_runtime()} | Threads: {active_threads}/{target_thread_count} | Generated: {generated_count} | Failed: {failed_count} | CPM: {cpm}"
    set_console_title(title)

def title_updater():
    while True:
        update_title()
        time.sleep(1)

def update_counter(reason):
    global generated_count, failed_count
    
    with lock:
        if reason == "generated":
            generated_count += 1
        elif reason == "failed":
            failed_count += 1

title_thread = threading.Thread(target=title_updater, daemon=True)
title_thread.start()

def input_thread_count():
    global target_thread_count
    while True:
        try:
            thread_count = input(f"\n{f.LIGHTBLUE_EX}  > Enter number of threads (1-20): {s.RESET_ALL}")
            if thread_count.isdigit():
                thread_count = int(thread_count)
                if 1 <= thread_count <= 20:
                    target_thread_count = thread_count
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return thread_count
                else:
                    fprint("Please enter a number between 1 and 20.")
            else:
                fprint("Invalid input. Only numbers are allowed.")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{f.RED}Program interrupted by user.")
            return None

def start_worker_thread(thread_id, worker_func):
    global thread_counter
    with threads_lock:
        thread = threading.Thread(target=worker_func, daemon=True)
        thread.start()
        threads_list.append(thread)
        thread_counter += 1

def thread_monitor(worker_func):
    global thread_restart_enabled, target_thread_count, thread_counter
    
    while thread_restart_enabled:
        with threads_lock:
            threads_list[:] = [t for t in threads_list if t.is_alive()]
            active_count = len(threads_list)
        
        if active_count < target_thread_count and thread_restart_enabled:
            for _ in range(target_thread_count - active_count):
                thread_counter += 1
                start_worker_thread(thread_counter, worker_func)
        
        if active_count == 0 and not thread_restart_enabled:
            break
            
        time.sleep(1)

def safe_print(message):
    with print_lock:
        print(message + s.RESET_ALL)
