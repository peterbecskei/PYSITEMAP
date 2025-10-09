import requests
import re
import os
import csv
from urllib.parse import urlparse

GETCONTENT =False
def load_urls(filename):
    urls = []
    try:
        with open(filename, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    urls.append(row[0].strip())
    except FileNotFoundError:
        pass
    return urls

def save_urls(filename, urls):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        for u in urls:
            writer.writerow([u])

def extract_links(html):
    pattern = r'https?://\S+|www\.\S+'
    links = re.findall(pattern, html)
    processed = []
    for link in links:
        if link.startswith('www.'):
            link = 'http://' + link
        processed.append(link)
    return processed

def save_content(url, html):
    p = urlparse(url)
    path_parts = [part for part in p.path.split('/') if part]
    if path_parts:
        dir_path = os.path.join(*path_parts)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, 'content.txt')
    else:
        file_path = 'content.txt'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

def fetch():
    initial_urls = load_urls('URL_LIST.csv')
    LISTURL = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    for url in initial_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(url, "OK")
                html = response.text
                if GETCONTENT:
                    save_content(url, html)
                new_links = extract_links(html)
                LISTURL.update(new_links)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    save_urls('URL_LIST2.csv', sorted(LISTURL))
    return LISTURL

def fetch2(LISTURL):
    level2_urls = load_urls('URL_LIST2.csv')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    for url in level2_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                html = response.text
                if GETCONTENT:
                    save_content(url, html)
                new_links = extract_links(html)
                LISTURL.update(new_links)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    save_urls('URL_LIST3.csv', sorted(LISTURL))
    return LISTURL

if __name__ == '__main__':
    print("MAIN stat")
    url2 = fetch()
    fetch2(url2)