# 🚀 Canton Coinflip BOT By Nightly Wallet

> Automated playing coinflip game and multi-account management

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/vonssy/Canton-Coinflip-BOT.svg)](https://github.com/vonssy/Canton-Coinflip-BOT/stargazers)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Proxy Recommendation](#proxy-recommendation)
- [Support](#support)
- [Contributing](#contributing)

## 🎯 Overview

Canton Coinflip BOT By Nightly Wallet is an automated tool designed to playing coinflip game across multiple accounts. It provides seamless offers robust proxy support for enhanced security and reliability.

**🔗 Get Started:** [Register on Coinflip By Nightly Wallet](https://coinflip.nightly.app/)

> **Important:** Connect with nightly wallet - canton chain.

## ✨ Features

- 🔄 **Automated Account Management** - Retrieve account information automatically
- 🌐 **Flexible Proxy Support** - Run with or without proxy configuration
- 🔀 **Smart Proxy Rotation** - Automatic rotation of invalid proxies
- 💰 **Initial Reward** - Automated claim initial credits reward
- ⏰ **Daily Faucet** - Automated claim daily faucet
- 🪙 **Play Coinflip** - Automated playing coinflip game
- 👥 **Multi-Account Support** - Manage multiple accounts simultaneously
- 🔔 **Telegram Notification** - Automatically send notifications on telegram bot father

## 📋 Requirements

- **Python:** Version 3.9 or higher
- **pip:** Latest version recommended
- **Compatible libraries:** eth-account and eth-utils (see requirements.txt)

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vonssy/Canton-Coinflip-BOT.git
cd Canton-Coinflip-BOT
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or for Python 3 specifically
pip3 install -r requirements.txt
```

### 3. Library Version Management

> ⚠️ **Important:** Ensure library versions match those specified in `requirements.txt`

**Check installed library version:**
```bash
pip show library_name
```

**Uninstall conflicting library:**
```bash
pip uninstall library_name
```

**Install specific library version:**
```bash
pip install library_name==version
```

## ⚙️ Configuration

### Account Setup

Create or edit `accounts.txt` in the project directory:

```
your_canton_nightly_private_key_1
your_canton_nightly_private_key_2
your_canton_nightly_private_key_3
```

### TG BOT Setup

Create or edit `.env` in the project directory (optional):

```
BET_SIZE=1
API_TOKEN=0123456789:xxxxxxxxxxxxx
CHAT_ID=9876543210
```

### Proxy Configuration (Optional)

Create or edit `proxy.txt` in the project directory:

```
# Simple format (HTTP protocol by default)
192.168.1.1:8080

# With protocol specification
http://192.168.1.1:8080
https://192.168.1.1:8080

# With authentication
http://username:password@192.168.1.1:8080
```

## 🚀 Usage

Run the bot using one of the following commands:

```bash
python bot.py
# or for Python 3 specifically
python3 bot.py
```

### Runtime Options

When starting the bot, you'll be prompted to choose:

1. **Proxy Mode Selection:**
   - Option `1`: Run with proxy
   - Option `2`: Run without proxy

2. **Auto-Rotation:** 
   - `y`: Enable automatic invalid proxy rotation
   - `n`: Disable auto-rotation

## 💖 Support the Project

If this project has been helpful to you, consider supporting its development:

### Cryptocurrency Donations

| Network | Address |
|---------|---------|
| **EVM** | `0xe3c9ef9a39e9eb0582e5b147026cae524338521a` |
| **TON** | `UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB` |
| **SOL** | `E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf` |
| **SUI** | `0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347` |

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. ⭐ **Star this repository** if you find it useful
2. 👥 **Follow** for updates on new features
3. 🐛 **Report issues** via GitHub Issues
4. 💡 **Suggest improvements** or new features
5. 🔧 **Submit pull requests** for bug fixes or enhancements

## 📞 Contact & Support

- **Developer:** vonssy
- **Issues:** [GitHub Issues](https://github.com/vonssy/Canton-Coinflip-BOT/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vonssy/Canton-Coinflip-BOT/discussions)

---

<div align="center">

**Made with ❤️ by [vonssy](https://github.com/vonssy)**

*Thank you for using Canton Coinflip BOT By Nightly Wallet! Don't forget to ⭐ star this repository.*

</div>