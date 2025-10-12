import re
import os
import csv
import requests
from urllib.parse import urljoin, urlparse


class SiteMapCommander:
    def __init__(self, base_url="https://www.zsu.hu", get_content=False):
        self.base_url = base_url
        self.get_content = get_content
        self.level1_links = []
        self.level2_links = []
        self.status = "Initialized"
        self.data_dir = "SITEMAP"
        self.level1_file = "level1Links.csv"
        self.level2_file = "level2Links.csv"

        # Create DATA directory if it doesn't exist
        if self.get_content and not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch0(self):
        """First-level content extraction"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            self.level1_links = self._extract_urls(response.text, self.base_url)

            # Save to CSV without duplicates
            self._save_to_csv(list(set(self.level1_links)), self.level1_file)
            self.status = f"Level 1 completed: {len(self.level1_links)} URLs found"
            print(self.status)
            # Save content if GETCONTENT is True
            if self.get_content:
                self._save_content(response.text, "1.txt")
                filename = f"level1_links.html"
                linkfilter = set()
                for urls in self.level1_links:
                    if urls.startswith('http'):
                        linkfilter.add(urls)
                self.level1_links = list(linkfilter)
                print(f"Filtered Level 1 links: {len(self.level1_links)}")

                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    for urls in self.level1_links:
                         if urls.startswith('http'):
                             #f.write(f'<a href="{urls}">{urls}</a><br>\n')
                             f.write(f'<a href="{urls}">{urls}</a><br>')


        except requests.RequestException as e:
            self.status = f"Level 1 error: {str(e)}"
            self.level1_links = []

    def fetch2(self):
        """Second-level content extraction"""
        if not self.level1_links and os.path.exists(self.level1_file):
            self._load_from_csv(self.level1_file, self.level1_links)

        if not self.level1_links:
            self.status = "No Level 1 links available for Level 2 crawling"
            return

        self.level2_links = []
        for idx, url in enumerate(self.level1_links, start=1):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                urls = self._extract_urls(response.text, url)
                self.level2_links.extend(urls)

                if self.get_content:
                    self._save_content(response.text, f"{idx}.txt")

            except requests.RequestException as e:
                self.status = f"Level 2 error for {url}: {str(e)}"
                continue

        # Save to CSV without duplicates
        self._save_to_csv(list(set(self.level2_links)), self.level2_file)
        self.status = f"Level 2 completed: {len(self.level2_links)} URLs found"

    def _extract_urls(self, text, base_url):
        """Extract URLs from text using regex"""
        # Convert relative URLs to absolute and filter valid URLs
        valid_urls = []
        #pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        pattern = r'"http[^"]*"'
        urls = re.findall(pattern, text)
        #print(urls)
        for url in urls:
            absolute_url = url.replace('"', '')
            parsed = urlparse(absolute_url)
            #print(url, absolute_url, parsed)
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                if parsed.netloc == urlparse(base_url).netloc:
                    valid_urls.append(absolute_url)
        #print(valid_urls)




        pattern = r'"/[^"]*"'
        paths = re.findall(pattern, text)
        #print(paths)


        for url in paths:
            urlfilt=url.replace('"/', '').replace('"', '')
            #print(url, urlfilt)
            #if urlfilt in ['/', '/""']:
            absolute_url = urljoin(base_url, urlfilt)
            parsed = urlparse(absolute_url)
            #print(url, absolute_url, parsed)
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                valid_urls.append(absolute_url)
        #print(valid_urls)



        return valid_urls


    def _save_to_csv(self, links, filename):
        """Save links to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for link in links:
                writer.writerow([link])

    def _load_from_csv(self, filename, link_list):
        """Load links from CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                link_list.extend([row[0] for row in reader if row])
        except FileNotFoundError:
            self.status = f"CSV file {filename} not found"

    def _save_content(self, content, filename):
        """Save webpage content to file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_data(self):
        """Return data structure"""
        return {
            "BASEURL": self.base_url,
            "level1Links": self.level1_links,
            "level2Links": self.level2_links,
            "GETCONTENT": self.get_content,
            "status": self.status
        }


# Example usage
if __name__ == "__main__":
    commander = SiteMapCommander()
    commander.fetch0()
    print(commander.get_data())
    commander.fetch2()
    print(commander.get_data())