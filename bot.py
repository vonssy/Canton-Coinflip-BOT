from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from base58 import b58decode
from base64 import b64decode, b64encode
from nacl.signing import SigningKey
from dotenv import load_dotenv
from datetime import datetime
from colorama import *
import asyncio, random, time, pytz, sys, re, os

load_dotenv()

wib = pytz.timezone('Asia/Jakarta')

class Canton:
    def __init__(self) -> None:
        self.API_URL = {
            "coinflip": "https://mainnet.rpc.canton.nightly.app",
            "explorer": "https://www.cantonscan.com/update/"
        }
        self.BET_SIZE = 1 # U can change it.
        self.HEADERS = {}
        self.USE_PROXY = False
        self.ROTATE_PROXY = False
        self.TG_TOKEN = os.getenv("TG_TOKEN")
        self.TG_CHAT_ID = os.getenv("TG_CHAT_ID")
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.accounts = {}
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Canton Coin Flip {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.txt"
        try:
            with open(filename, 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
            return None
    
    def load_tg_tokens(self):
        filename = "telegram_token.txt"
        try:
            with open(filename, 'r') as file:
                telegram_token = file.readline().strip()
            return telegram_token
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
            return None

    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"
    
    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"

        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)

        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]

        return proxy_url
    
    def initialize_headers(self, pub_key: str):
        if pub_key not in self.HEADERS:
            self.HEADERS[pub_key] = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Host": "mainnet.rpc.canton.nightly.app",
                "Origin": "https://coinflip.nightly.app",
                "Pragma": "no-cache",
                "Referer": "https://coinflip.nightly.app/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": random.choice(self.USER_AGENTS)
            }

        account_data = self.accounts.get(pub_key)
        if account_data and account_data.get("token"):
            self.HEADERS[pub_key]["Authorization"] = f"Bearer {account_data['token']}"

        return self.HEADERS[pub_key].copy()
    
    def gen_pubkey(self, private_key: str):
        try:
            key_bytes = b58decode(private_key)

            if len(key_bytes) != 64: return None

            pub_bytes = key_bytes[32:]
            return b64encode(pub_bytes).decode()
        except Exception as e:
            return None

    def gen_signature(self, private_key: str, message: str):
        try:
            key_bytes = b58decode(private_key)

            if len(key_bytes) != 64: return None

            seed_bytes = key_bytes[:32]

            signing_key = SigningKey(seed_bytes)
            message_bytes = b64decode(message)
            signed = signing_key.sign(message_bytes)
            return b64encode(signed.signature).decode()
        except Exception as e:
            return None

    def gen_payload(self, private_key: str, challenge: dict):
        try:
            challenge_id = challenge.get("challengeId")
            message = challenge.get("challenge")

            return {
                "publicKey": self.gen_pubkey(private_key),
                "challengeId": challenge_id,
                "signature": self.gen_signature(private_key, message)
            }
        except Exception as e:
            raise Exception(f"Failed to Generate Payload")

    def mask_account(self, account):
        try:
            mask_account = account[:12] + '*' * 8 + account[-12:]
            return mask_account
        except Exception as e:
            return None

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1  or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1  or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return self.USE_PROXY, self.ROTATE_PROXY
    
    async def ensure_ok(self, response):
        if response.status >= 400:
            error_text = await response.text()
            raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def check_connection(self, proxy_url=None):
        url = "https://api.ipify.org?format=json"

        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=url, proxy=proxy, proxy_auth=proxy_auth) as response:
                    await self.ensure_ok(response)
                    return True
        except (Exception, ClientResponseError, TimeoutError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def send_telegram(self, text: str):
        url = f"https://api.telegram.org/bot{self.TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": self.TG_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                async with session.post(url, json=payload) as resp:
                    return await resp.text()
        except Exception as e:
            self.log(f"Telegram Error: {e}")
    
    async def auth_challenge(self, pub_key: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/auth/challenge"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)
                headers["Content-Type"] = "application/json"
                payload = {
                    "publicKey": pub_key
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Auth Challenge {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def auth_verify(self, private_key: str, pub_key: str, challenge: dict, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/auth/verify"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)
                headers["Content-Type"] = "application/json"
                payload = self.gen_payload(private_key, challenge)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def get_party_id(self, pub_key: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/me"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Party Id:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Party Id {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def perfrom_checkin(self, pub_key: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/performDailyCheckIn"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def escrow_state(self, pub_key: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/queryEscrowState"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}State   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch State {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def req_initial_reward(self, pub_key: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/requestInitialReward"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Initial Reward   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Claim {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def play_coin_flip(self, pub_key: str, bet_size: int, proxy_url=None, retries=5):
        url = f"{self.API_URL['coinflip']}/playEscrowCoinFlip"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(pub_key)
                headers["Content-Type"] = "application/json"
                payload = {
                    "betSize": bet_size
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError, TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Flip {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, pub_key: str, proxy_url: None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(pub_key)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.display_proxy(proxy_url)} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True

            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(pub_key)
                await asyncio.sleep(1)
                continue

            return False
    
    async def process_login(self, private_key: str, pub_key: str, proxy_url=None):
        is_valid = await self.process_check_connection(pub_key, proxy_url)
        if not is_valid: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(pub_key)

        if pub_key not in self.accounts:
            self.accounts[pub_key] = {'private_key': private_key}

            challenge = await self.auth_challenge(pub_key, proxy_url)
            if not challenge: return False

            verify = await self.auth_verify(private_key, pub_key, challenge)
            if not verify: return False

            self.accounts[pub_key]['expires'] = verify.get("expiresAt")
            self.accounts[pub_key]['token'] = verify.get("token")

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
            )

        if int(time.time()) > self.accounts[pub_key].get('expires', 0):
            challenge = await self.auth_challenge(pub_key, proxy_url)
            if not challenge: return False

            verify = await self.auth_verify(private_key, pub_key, challenge)
            if not verify: return False

            self.accounts[pub_key]['expires'] = verify.get("expiresAt")
            self.accounts[pub_key]['token'] = verify.get("token")

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
            )

        return self.accounts[pub_key]
    
    async def process_accounts(self, private_key: str, pub_key: str, proxy_url=None):
        loginned = await self.process_login(private_key, pub_key, proxy_url)
        if not loginned: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(pub_key)

        party_id = await self.get_party_id(pub_key, proxy_url)
        if not party_id: return False

        address = party_id.get("partyId")

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Party Id:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
        )

        state = await self.escrow_state(pub_key, proxy_url)
        if not state: return False

        contract_id = state.get("contractId")
        total_credits = state.get("totalCredits")
        available_credits = state.get("availableCredits")
        credits_used = state.get("creditsUsed")
        initial_reward_claimed = state.get("initialRewardClaimed")

        self.log(f"{Fore.CYAN+Style.BRIGHT}State   :{Style.RESET_ALL}")
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Total Credits    :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {total_credits} © {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Available Credits:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {available_credits} © {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Credits Used     :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {credits_used} © {Style.RESET_ALL}"
        )

        if initial_reward_claimed:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Initial Reward   :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
            )
        else:
            req_rewards = await self.req_initial_reward(pub_key, proxy_url)
            if not req_rewards: return False

            msg = req_rewards.get("message")

            if not req_rewards.get("success"):
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Initial Reward   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )
                return False
            
            contract_id = req_rewards.get("state", {}).get("contractId")
            total_credits = req_rewards.get("state", {}).get("totalCredits")
            available_credits = req_rewards.get("state", {}).get("availableCredits")
            credits_used = req_rewards.get("state", {}).get("creditsUsed")
            
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Initial Reward   :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {msg} {Style.RESET_ALL}"
            )

        self.log(f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}")

        checkin = await self.perfrom_checkin(pub_key, proxy_url)
        if checkin:
            msg = checkin.get("message")

            if checkin.get("success"):
                tx_hash = checkin.get("txHash")

                if tx_hash:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Tx Hash :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Explorer:{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {self.API_URL['explorer']}{tx_hash} {Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )
    
        self.log(f"{Fore.CYAN+Style.BRIGHT}CoinFlip:{Style.RESET_ALL}")

        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Payout  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.BET_SIZE} © {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Credits :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {available_credits} © {Style.RESET_ALL}"
        )

        if available_credits < self.BET_SIZE:
            self.accounts[pub_key]['credits'] = 0
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient Credits {Style.RESET_ALL}"
            )
            return False
        
        self.accounts[pub_key]['credits'] = available_credits

        flip = await self.play_coin_flip(pub_key, self.BET_SIZE, proxy_url)
        if not flip: return False

        msg = flip.get("message", "Unknown")

        if not flip.get("success"):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Failed to Flip {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
            )
            return False

        user_won = flip.get("userWon")
        outcome = flip.get("outcome")
        tx_hash = flip.get("txHash")
        available_credits_after = flip.get("escrowState", {}).get("availableCredits")
        
        if available_credits_after is not None:
            self.accounts[pub_key]['credits'] = available_credits_after

        if user_won:
            msg_color = Fore.GREEN
            msg_str = "WON"
        else:
            msg_color = Fore.RED
            msg_str = "LOSE"

        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Outcome :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {outcome} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
            f"{msg_color+Style.BRIGHT} {msg_str} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Message :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {msg} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Tx Hash :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Explorer:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.API_URL['explorer']}{tx_hash} {Style.RESET_ALL}"
        )

    async def print_statistics(self):
        separator = "=" * 60
        self.log(f"{Fore.CYAN+Style.BRIGHT}{separator}{Style.RESET_ALL}")
        
        accounts_with_credits = {k: v for k, v in self.accounts.items() if 'credits' in v}
        
        if not accounts_with_credits:
            self.log(f"{Fore.YELLOW+Style.BRIGHT}No account statistics available yet.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN+Style.BRIGHT}{separator}{Style.RESET_ALL}")
            return []
        
        total_accounts = len(accounts_with_credits)
        inactive_accounts = sum(1 for v in accounts_with_credits.values() if v.get('credits', 0) == 0)
        active_accounts = total_accounts - inactive_accounts
        total_available_credits = sum(v.get('credits', 0) for v in accounts_with_credits.values())
        
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}Total Accounts   :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {total_accounts} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}Active Accounts  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} {active_accounts} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}Inactive Accounts:{Style.RESET_ALL}"
            f"{Fore.RED+Style.BRIGHT} {inactive_accounts} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}Total Credits    :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {total_available_credits} © {Style.RESET_ALL}"
        )

        if self.TG_TOKEN and self.TG_CHAT_ID:
            msg = (
                f"<b>📊 CANTON COINFLIP BOT STATISTICS</b>\n\n"
                f"<pre>"
                f"─────────────────────────────────────\n"
                f"👥 Total Accounts     : {total_accounts}\n"
                f"🟢 Active Accounts    : {active_accounts}\n"
                f"🔴 Inactive Accounts  : {inactive_accounts}\n"
                f"💰 Total Credits      : {total_available_credits} ©\n"
                f"─────────────────────────────────────"
                f"</pre>"
            )

            await self.send_telegram(msg)

        return [pub_key for pub_key, data in self.accounts.items() if data.get('credits', -1) == 0]

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts: return

            self.print_question()
            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if self.USE_PROXY: self.load_proxies()

            for private_key in accounts:
                pub_key = self.gen_pubkey(private_key)
                if pub_key and pub_key not in self.accounts:
                    self.accounts[pub_key] = {'private_key': private_key}

            separator = "=" * 25
            while True:
                current_accounts = [(k, v['private_key']) for k, v in self.accounts.items() if 'private_key' in v]
                
                for idx, (pub_key, private_key) in enumerate(current_accounts, start=1):
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(current_accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Pub Key :{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(pub_key)} {Style.RESET_ALL}"
                    )

                    if not pub_key:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Invalid Private Key {Style.RESET_ALL}"
                        )
                        continue

                    await self.process_accounts(private_key, pub_key)
                    await asyncio.sleep(random.uniform(1.5, 3.0))

                await self.print_statistics()
                
                remaining_accounts = [k for k, v in self.accounts.items() if 'private_key' in v]
                if not remaining_accounts:
                    self.log(
                        f"{Fore.RED+Style.BRIGHT}All accounts have 0 credits. Stopping bot.{Style.RESET_ALL}"
                    )
                    break

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e
        except asyncio.CancelledError:
            raise

if __name__ == "__main__":
    try:
        bot = Canton()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Canton Coin Flip - BOT{Style.RESET_ALL}                                       "                              
        )
    finally:
        sys.exit(0)