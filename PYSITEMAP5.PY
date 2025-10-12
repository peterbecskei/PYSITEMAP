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

"""

from __future__ import annotations
import requests
import re
import csv
import os
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from typing import List, Set, Dict


class SiteMapCommander:
    def __init__(self, config: Dict = None):
        defaults = {
            "BASEURL": "https://www.companywall.hu/SiteMap/Companies?p=1110",
            "level1Links": [],
            "level2Links": [],
            "GETCONTENT": True,
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
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
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
    #smc.fetch0()
    print(smc.config['status'])
    print("Running fetch2() from level1Links.csv")
    smc.fetch2()
    print(smc.config['status'])
