"""
Site Map Commander
Author: ChatGPT

A clean, minimal Python implementation for multi-level site mapping and content extraction.

Core config dictionary (self.config):
  - BASEURL (str): default 'https://www.idokep.hu/'
  - level1Links (list): populated by fetch0()
  - level2Links (list): populated by fetch2()
  - GETCONTENT (bool): whether to save response bodies into DATA/ as 'ID.txt'
  - status (str): last operation message

Files produced:
  - level1Links.csv
  - level2Links.csv
  - DATA/{N}.txt  (if GETCONTENT is True)

Notes:
  - Respects robots.txt per-host before fetching content.
  - Minimal dependencies: requests, re, csv, os, urllib.parse, urllib.robotparser
  - Timeouts included; faulty URLs are skipped.

Usage:
  commander = SiteMapCommander()
  commander.fetch0()  # level-1 crawl from BASEURL
  commander.fetch2()  # level-2 crawl from level1Links.csv
zg
"""

from __future__ import annotations
import requests
import re
import csv
import os
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from typing import List, Set, Dict
import urllib.parse
import time




#proxys = ['8.219.97.248:80', '47.90.205.231:33333', '5.252.33.13:2025', '211.230.49.122:3128', '198.187.28.126:8080', '202.152.44.18:8081', '198.54.124.88:8080', '66.201.7.213:3128', '199.188.207.30:8080', '45.149.115.145:8888', '159.89.25.162:8080', '31.162.53.69:1080', '143.92.61.148:8082', '113.183.43.123:8080', '198.54.123.134:8080', '52.188.28.218:3128', '54.226.156.148:20201', '43.134.177.187:20201', '143.198.147.156:8888', '210.87.125.146:8090', '129.226.207.13:20201', '65.108.203.35:28080', '34.222.65.100:1976', '200.174.198.158:8888', '178.17.62.152:8881', '147.75.34.105:443', '52.47.164.226:9304', '188.166.230.109:31028', '65.108.159.129:8081', '179.27.158.78:80', '67.43.228.253:3881', '93.177.66.204:19000', '135.125.97.184:46107', '116.105.27.106:10040', '18.143.167.190:9947', '78.12.249.123:8026', '72.10.164.178:2493', '34.216.224.9:12542', '123.128.12.93:9050', '72.10.160.170:13701', '8.220.205.172:80', '72.10.160.173:24063', '148.178.124.75:8888', '43.129.234.168:1080', '190.242.157.215:8080', '190.145.194.210:8080', '140.238.184.182:3128', '23.237.210.82:80', '200.85.167.254:8080', '186.180.73.50:9090', '8.211.195.173:9080', '94.141.118.130:1080', '67.43.228.251:9105', '67.43.236.18:3927', '102.22.193.35:8080', '199.188.207.170:8080', '47.79.91.116:1122', '120.92.211.211:7890', '103.54.218.74:8080', '162.243.149.86:31028', '39.99.34.28:8888', '72.10.160.90:1237', '91.205.172.113:3120', '45.174.94.26:999', '45.70.236.121:8080', '103.56.206.67:4000']
#proxys = ['8.219.97.248:80', '47.90.205.231:33333', '5.252.33.13:2025', '211.230.49.122:3128', '198.187.28.126:8080', '202.152.44.18:8081', '66.201.7.213:3128', '199.188.207.30:8080', '45.149.115.145:8888', '159.89.25.162:8080', '31.162.53.69:1080', '143.92.61.148:8082', '113.183.43.123:8080', '198.54.123.134:8080', '52.188.28.218:3128', '54.226.156.148:20201', '43.134.177.187:20201', '210.87.125.146:8090', '65.108.203.35:28080', '34.222.65.100:1976', '200.174.198.158:8888', '147.75.34.105:443', '52.47.164.226:9304', '65.108.159.129:8081', '67.43.228.253:3881', '135.125.97.184:46107', '18.143.167.190:9947', '78.12.249.123:8026', '34.216.224.9:12542', '72.10.160.170:13701', '8.220.205.172:80', '148.178.124.75:8888', '190.242.157.215:8080', '140.238.184.182:3128', '23.237.210.82:80', '200.85.167.254:8080', '186.180.73.50:9090', '8.211.195.173:9080', '67.43.228.251:9105', '102.22.193.35:8080', '199.188.207.170:8080', '120.92.211.211:7890', '162.243.149.86:31028', '72.10.160.90:1237', '91.205.172.113:3120', '45.70.236.121:8080', '103.56.206.67:4000']
#proxys = ['47.90.205.231:33333', '5.252.33.13:2025', '211.230.49.122:3128', '202.152.44.18:8081', '66.201.7.213:3128', '199.188.207.30:8080', '45.149.115.145:8888', '159.89.25.162:8080', '31.162.53.69:1080', '143.92.61.148:8082', '198.54.123.134:8080', '52.188.28.218:3128', '54.226.156.148:20201', '43.134.177.187:20201', '210.87.125.146:8090', '65.108.203.35:28080', '34.222.65.100:1976', '200.174.198.158:8888', '52.47.164.226:9304', '67.43.228.253:3881', '18.143.167.190:9947', '78.12.249.123:8026', '34.216.224.9:12542', '8.220.205.172:80', '190.242.157.215:8080', '140.238.184.182:3128', '23.237.210.82:80', '200.85.167.254:8080', '186.180.73.50:9090', '8.211.195.173:9080', '102.22.193.35:8080', '199.188.207.170:8080', '162.243.149.86:31028', '91.205.172.113:3120', '103.56.206.67:4000']
#proxys = ['47.90.205.231:33333', '5.252.33.13:2025', '211.230.49.122:3128', '202.152.44.18:8081', '66.201.7.213:3128', '199.188.207.30:8080', '45.149.115.145:8888', '159.89.25.162:8080', '31.162.53.69:1080', '143.92.61.148:8082', '198.54.123.134:8080', '52.188.28.218:3128', '54.226.156.148:20201', '43.134.177.187:20201', '210.87.125.146:8090', '65.108.203.35:28080', '34.222.65.100:1976', '200.174.198.158:8888', '52.47.164.226:9304', '18.143.167.190:9947', '78.12.249.123:8026', '34.216.224.9:12542', '190.242.157.215:8080', '140.238.184.182:3128', '23.237.210.82:80', '200.85.167.254:8080', '186.180.73.50:9090', '8.211.195.173:9080', '199.188.207.170:8080', '91.205.172.113:3120']
proxys = []
i = 0

urlprox= requests.get("https://free-proxy-list.net/en/ssl-proxy.html", timeout=10)
#print(urlprox.text)
pattern = r'Free proxies from free-proxy-list\.net(.*?)</textarea>'
match = re.search(pattern, urlprox.text, re.DOTALL)

if match:
    proxy_block = match.group(1).strip()

    # Soronként feldolgozás
    PROXI_LIST = []
    for line in proxy_block.split('\n'):
        line = line.strip()
        # Csak az IP:Port formátumú sorok
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', line):
            PROXI_LIST.append(line)

    status = f"Extracted {len(PROXI_LIST)} proxies"
    print(f"Status: {status}")
print(PROXI_LIST)
print(proxys)
proxys=PROXI_LIST[:40]
while i < len(proxys):
    proxy =  proxys[i % len(proxys)]

    print(f"{time.strftime('%H:%M:%S')} - Using: {proxy}     {i},  {i % len(proxys)}, len={len(proxys)}")
    prox = f"http://{proxy}"
    try:
        #r = requests.get("http://httpbin.org/ip", proxies={"http": prox, "https": prox}, timeout=10)
        r= requests.get("https://www.companywall.hu/v%C3%A1llalat/negy-gulyas-kft/MMIrysID", proxies={"http": prox, "https": prox}, timeout=2)

        #print(f"IP: {r.json()['origin']}")
    except:
        print("Failed")
        proxys.remove(proxy)

    #time.sleep(60)
    i += 1
print(f"Using {len(proxys)} proxies")
print(proxys)

class SiteMapCommander:
    def __init__(self, config: Dict = None):
        defaults = {
            "BASEURL": "https://www.companywall.hu/SiteMap/Companies?p=1000",
            "level1Links": [],
            "level2Links": [],
            "GETCONTENT": True,
            "proxied" : True,
            "status": "Initialized",
        }
        self.config = defaults if config is None else {**defaults, **config}

        self.level1_csv = "level1Link.csv"
        self.level2_csv = "level2Link.csv"
        self.data_folder = "LINKS_DATA"
        self.user_agent = "SiteMapCommander/1.0 (+https://example.com)"
        self.timeout = 10  # seconds

        # robots.txt parsers cache per netloc
        self._robots_cache: Dict[str, RobotFileParser] = {}

        # Ensure storage
        self._ensure_data_folder()

    # ------------------ Helpers ------------------
    def _ensure_data_folder(self):
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def _load_csv(self, path: str) -> List[str]:
        if not os.path.exists(path):
            return []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = [r[0].strip() for r in reader if r]
        return rows

    def _save_csv(self, path: str, urls: List[str]):
        # write unique, sorted for determinism
        unique = sorted(set(urls))
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for u in unique:
                writer.writerow([u])

    def _next_data_id(self) -> int:
        # files named like '1.txt', '2.txt', ...
        existing = [p for p in os.listdir(self.data_folder) if p.endswith(".txt")]
        nums = []
        for name in existing:
            try:
                nums.append(int(os.path.splitext(name)[0]))
            except ValueError:
                continue
        return max(nums) + 1 if nums else 1

    def _extract_links(self, html: str, base_url: str) -> Set[str]:
        # match absolute http(s), www., or relative paths starting with '/'
        pattern = r"(https?://[^\s'\"<>]+|www\.[^\s'\"<>]+|/[^\s'\"<>]+)"
        raw = re.findall(pattern, html)
        out = set()
        for link in raw:
            # normalize
            if link.startswith("www."):
                link = "http://" + link
            abs_link = urljoin(base_url, link)
            # strip fragments
            parsed = urlparse(abs_link)
            clean = parsed._replace(fragment="").geturl()
            out.add(clean)
        return out

    def _get_robots_parser(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        netloc = parsed.scheme + "://" + parsed.netloc
        if netloc in self._robots_cache:
            return self._robots_cache[netloc]
        robots_url = urljoin(netloc, "/robots.txt")
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception:
            # on failure, default to allow everything to avoid blocking entirely
            rp = RobotFileParser()
            rp.parse(())
        self._robots_cache[netloc] = rp
        return rp

    def _is_allowed(self, url: str) -> bool:
        try:
            rp = self._get_robots_parser(url)
            parsed = urlparse(url)
            path = parsed.path or "/"
            return rp.can_fetch(self.user_agent, path)
        except Exception:
            # if robots fails, be conservative and disallow
            return False

    def _fetch(self, url: str) -> str:
        headers = {"User-Agent": self.user_agent}
        try:
            proxied_url = 'https://api.allorigins.win/raw?url=' + urllib.parse.quote(url)
            if self.config.get("proxied") : proxied_url=url
            print(proxied_url, self.config.get("proxied"))

            #proxy_url = f"http://{proxy_ip}:{proxy_port}"

            #pid = self._next_data_id() % len(proxys)
            #print(pid)
            proxy_url = f"http://{proxys[hash(url)%len(proxys)]}"
            #proxy_url = f"http://{proxys[pid]}"

            print(proxy_url)
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }

            resp = requests.get(proxied_url, headers=headers, proxies=proxies, timeout=self.timeout)
            resp.raise_for_status()
            print(f"Fetched {url} (size: {len(resp.text)}), status: {resp.status_code}")

            return resp.text
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}")

    # ------------------ Public API ------------------
    def fetch0(self):
        """Fetch BASEURL, extract level-1 links, save CSV and optionally save content."""
        base = self.config["BASEURL"]
        self.config["status"] = f"Starting fetch0 from {base}"
        try:
            if not self._is_allowed(base):
                self.config["status"] = f"Blocked by robots.txt: {base}"
                return
            html = self._fetch(base)
        except Exception as e:
            self.config["status"] = str(e)
            return

        links = self._extract_links(html, base)

        # Save level1 links (unique, skip empty)
        links = {l for l in links if l}
        self.config["level1Links"] = sorted(links)
        self._save_csv(self.level1_csv, list(self.config["level1Links"]))

        # Optionally save content
        if self.config.get("GETCONTENT", True):
            nid = self._next_data_id()
            fname = os.path.join(self.data_folder, f"{nid}.txt")
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(html)
            except Exception as e:
                # don't fail the entire run
                self.config["status"] = f"Saved links but failed to save content: {e}"
                return
            if nid == 1:
                # if first file, save a simple HTML with links
                linkfile = os.path.join(self.data_folder, "Level1_links.html")
                try:
                    with open(linkfile, "w", encoding="utf-8") as f:
                        for url in self.config["level1Links"]:
                            f.write(f'<a href="{url}">{url}</a><br>\n')
                except Exception:
                    pass  # non-critical

        self.config["status"] = f"fetch0 completed: found {len(self.config['level1Links'])} links"

    def fetch2(self):
        """Process URLs from level1Links.csv, extract level-2 links, save CSV, optionally save contents."""
        self.config["status"] = "Starting fetch2"
        level1 = self._load_csv(self.level1_csv)
        if not level1:
            self.config["status"] = "No level1 links found; run fetch0() first or provide level1Links.csv"
            return

        all_level2: Set[str] = set()
        saved_count = 0
        nid = self._next_data_id()

        for url in level1:
            # Basic validation
            print(nid, url)
            if not url or not url.startswith("http"):
                continue
            # robots.txt check for this URL
            if not self._is_allowed(url):
                # skip but keep the link discovery behavior
                continue
            try:
                html = self._fetch(url)
            except Exception:
                # skip faulty URL
                continue
            links = self._extract_links(html, url)
            all_level2.update(links)

            if self.config.get("GETCONTENT", True):
                try:
                    fname = os.path.join(self.data_folder, f"{nid}.txt")
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(html)
                    nid += 1
                    saved_count += 1
                except Exception:
                    # continue but note failure
                    pass

        # Remove duplicates and save
        all_level2 = {l for l in all_level2 if l}
        self.config["level2Links"] = sorted(all_level2)
        self._save_csv(self.level2_csv, list(self.config["level2Links"]))

        self.config["status"] = f"fetch2 completed: found {len(self.config['level2Links'])} unique links; saved {saved_count} pages"


if __name__ == "__main__":
    # simple example run
    smc = SiteMapCommander()
    print("Running fetch0() from", smc.config['BASEURL'])
    smc.fetch0()
    print(smc.config['status'])
    print("Running fetch2() from level1Links.csv")
    #smc.fetch2()
    print(smc.config['status'])
