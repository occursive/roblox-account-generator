import random, string
from datetime import datetime
from colorama import Fore as f, Style as s
from threading import Lock

lock = Lock()

def time():
    return datetime.now().strftime("%H:%M:%S")

def color_print(label, label_color, text_color, text):
    with lock:
        print(f"{label_color}[{label}]{f.WHITE} - {f.LIGHTBLACK_EX}{time()} » {text_color}{text}{s.RESET_ALL}")
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

def get_proxy(proxy_type):
    if proxy_type.lower() == "http":
        scheme = "http://"
    elif proxy_type.lower() == "socks5":
        scheme = "socks5://"
    else:
        fprint("Invalid proxy type! Only 'http' or 'socks5' are supported. You can modify this in 'input/config.json'.")
        return None
    try:
        with open("input/proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        fprint("Could not find the file 'input/proxies.txt'. Please make sure it exists and contains your proxies.")
        return None
    if not proxies:
        fprint("The file input/proxies.txt is empty. Please add at least one proxy in the following format: ip:port@username:password.")
        return None
    return scheme + random.choice(proxies)

def generate_username():
    roots = ["zarn", "milo", "trev", "kayn", "luro", "jex", "naro", "vask", "dren", "xilo",
            "rilo", "synd", "quav", "bray", "tarn", "zayv", "lom", "fayr", "keld", "rix",
            "tharn", "vynz", "calo", "dran", "zelv", "fray", "nyro", "bex", "krev", "jorn",
            "sarn", "vex", "kryn", "drax", "lyn", "zor", "velk", "garo", "phin", "trex"]
    mods = ["flux", "dyn", "vyn", "stral", "grim", "lok", "vorn", "pran", "kaze", "thal",
            "myrk", "jinn", "zern", "cray", "vohl", "drux", "blen", "snok", "quen", "vrak",
            "zelk", "fryn", "nox", "brak", "skel", "throx", "drax", "vok", "kran", "morn"]
    ends = ["", "", "", str(random.randint(10,99)), str(random.randint(100,999)), str(random.randint(2005,2024)),
            "ix", "or", "en", "um", "ax", "ul", "ev", "ar", "us", "et"]
    u = random.choice(roots).capitalize() + random.choice(mods)
    if random.random() < 0.5: u += random.choice(ends)
    for a, b in [("a","4"), ("i","1"), ("o","0"), ("e","3")]:
        if random.random() < 0.25: u = u.replace(a, b)
    if len(u) < 15: u += str(random.randint(100,999))
    return u[:20]

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