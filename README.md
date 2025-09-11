<div align="center">
  <img src="https://github.com/user-attachments/assets/18b3293c-315b-4538-9614-d3e162994e8a" width="100"/>
</div>


<div align="center">
  
# Roblox Account Generator
</div>


<div align="center"> 

![showcase](https://github.com/user-attachments/assets/1b8aa934-2dcf-4556-8485-1636a305f7f8)

<p align="center">
  <br />
  <a href="https://discord.gg/2ZVpYAEEX8"><img src="https://img.shields.io/badge/Discord%20Server-Join%20Community-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /></a>
  <br />
  <br />
  <a href="https://t.me/occursive"><img src="https://img.shields.io/badge/Developer-@occursive-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Developer" /></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://t.me/occursivenews"><img src="https://img.shields.io/badge/📢%20News-@occursivenews-0088CC?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram News" /></a>
</p>
</div>


## 🔥 Features
- **Fully request-based**
- **Advanced TLS spoofing**
- **High-performance multi-threading**
- **Automatic failure protection**
- **Proxy Support**
- **Email verify support**
- **Avatar auto-change (after reaching stars)**

> [!NOTE]
> The tool supports funcaptcha solver from [Rosolve](https://rosolve.pro/) and email verification using a free temporary email service ([priyo.email](https://v3.priyo.email/)). If you need integration with a different captcha solver or email verification provider, contact me.

## ✍️ Usage
1. **Run** `pip install -r requirements.txt`
2. **Configure** `config.json`:
    - **Add** your RoSolve API key to `api_keys`
    - **Set** `custom_password` to `true` and add your password ***(optional)***
    - **Set** `email_verification` to `true` to verify generated accounts with email ***(optional)***
3. **Put** your proxies in `input/proxies.txt` *(username:password@host:port)*
4. **Run** python main.py
5. **If you like it, give a ⭐️ star to the repo**


## ⚙️ Configuration
```json
{
    "proxy_type": "http",                    // Proxy protocol to use (currently only "http" is supported)

    "custom_password": {                     // Custom password configuration for account creation
        "enabled": false,                    // Enable/disable custom password (true/false)
        "password": "$password123"           // Your custom password (min 8, max 200 characters)
    },

    "captcha_settings": {                    // CAPTCHA solver configuration
        "api_keys": {                        // API keys for different solvers
            "rosolve": ""                    // Your RoSolve API key (get from rosolve.pro)
        },
        "selected_solver": "rosolve",        // Active solver (currently only "rosolve" is supported)
        "timeout": 30                        // Solver timeout in seconds (10-120)
    },

    "email_verification": false              // Enable/disable email verification (true/false)
}
```

## 📁 Output
**All created accounts will be saved in the `output/accounts.txt` file in this format:**
```
userid:username:password:cookie
```
**If email verification is enabled, successfully verified accounts will be saved in `output/verified_accounts.txt` in this format:**
```
userid:username:email:password:cookie
```

## ✨ Stars to unlock
- ⭐️ **20 stars: Email verification** - 🎉 *UNLOCKED!*
- ⭐️ **50 stars: Change display name after creation** - ⏳ *COMING SOON!*
- ⭐️ **85 stars: Join group after creation**
- ⭐️ **100 stars: Change avatar after creation**
- ⭐️ **140 stars: Follow user after creation**
- ⭐️ **150+ stars: Your ideas**

> [!TIP]
> If you have custom ideas, share them in the `#suggestion` channel on my [Discord server](https://discord.gg/2ZVpYAEEX8).
  

## ⚠️ Disclaimer
> [!WARNING]
> This project is for educational purposes only. The author is not responsible for any misuse of this software.

## 📞 Contact

**Need support or a custom solution? Contact me:**

```
Telegram: https://t.me/occursive

Discord: @occursive

Discord server: https://discord.gg/2ZVpYAEEX8
```

---

<div align="center">
  
  **⭐ Star this repository if you find it useful!**
  
</div>
