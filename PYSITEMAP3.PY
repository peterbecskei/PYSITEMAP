import requests
import re
import os
import csv
from urllib.parse import urlparse
import urllib.parse

cwd = os.getcwd()
print(cwd)
DATAFOLDER = cwd + "\DATA\\"
print(DATAFOLDER)
if not os.path.exists(DATAFOLDER):
    os.makedirs(DATAFOLDER)
BASEURL = ""
GETCONTENT = True
URLID = 0
PROXED = False
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
            if u.startswith(BASEURL[:10]):
                writer.writerow([u])
    print(f"Saved {len(urls)} URLs to {filename}")

def extract_links(html):
    pattern = r'https?://\S+|www\.\S+'
    #pattern ="https?:\ / \ /[^ \s <> "']+)";
    processed = []
    matches = re.findall(r'"(.+?)"', html)
    print(matches)
    for match in matches:
        if match.startswith('http://') or match.startswith('https://') or match.startswith('www.') or match.startswith('/'):
            #print(match)
            processed.append(match)
    # This will find all substrings enclosed in double quotes

    # matches is now ['String 1', 'String 2', 'String3']
    #return ",".join(matches)
    #pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
    #pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[/\w\.-]*\??[/\w\.-=&%#]*)?'

    #links = re.findall(pattern, html)

    print(BASEURL)

    print(len(processed))
    for link in processed:
        if link.startswith('/'):
            link = BASEURL + link
            print(link)
            #processed.append(link)
        if link.startswith('www.'):
            link = 'http://' + link
            #processed.append(link)

        #pathpattern = r'[/\w\.-]*'
        #path=re.findall(pathpattern, link)
        #print(path)
    #    if link.startswith('www.'):
    #        link = 'http://' + link
    #        processed.append(link)
    #    if link.startswith('/'):
    #        link = BASEURL + link
    #        print(link)
        #if link.startswith(BASEURL[:15]) : # and link not in processed:
    #        processed.append(link)
 #           print(link)
        #processed.append(link)

    return processed

def save_content(url, html):
    global URLID
    URLID = URLID + 1
    p = urlparse(url)

   # path_parts = [part for part in p.path.split('/') if part]
   # if path_parts:
   #     dir_path = os.path.join(*path_parts)
    #    os.makedirs(dir_path, exist_ok=True)
    #    file_path = os.path.join(dir_path, 'content.txt')
    #else:
    #    file_path = 'content.txt'
    file_path = DATAFOLDER +   str(URLID) + '.txt'
    file_path = DATAFOLDER +   str(URLID) + '.html'

    print(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

def fetch0():
    initial_url = 'https://idokep.hu'
    BASEURL = initial_url
    LISTURL = set()


    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    url=initial_url
        #BASEURL = url
    print(BASEURL)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(url, "OK")
            print(BASEURL)
            #pathpattern = r'[/\w\.-]*'
            #path = re.findall(pathpattern, url)
            #print(path)

            html = response.text
            if GETCONTENT: save_content(url, html)
            new_links = extract_links(html)
            LISTURL.update(new_links)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    #save_urls('URL_LIST2.csv', sorted(LISTURL))
    save_urls('URL_LIST.csv', LISTURL)
    return LISTURL


def fetch():
    initial_urls = load_urls('URL_LIST.csv')
    LISTURL = set()
    global BASEURL


    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    for url in initial_urls:
        BASEURL = url
        # Assuming the original URL is stored in a variable named 'original_url'
        #original_url = "https://example.com"  # Replace with your actual URL
        proxied_url = 'https://api.allorigins.win/raw?url=' + urllib.parse.quote(url)
        if not PROXED:
            proxied_url = url
        print(proxied_url)
        try:
            response = requests.get(proxied_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(url, "OK")
                print(BASEURL)
                pathpattern = r'[/\w\.-]*'
                #path = re.findall(pathpattern, url)
                #print(path)

                html = response.text
                if GETCONTENT:

                    save_content(url, html)
                new_links = extract_links(html)
                LISTURL.update(new_links)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    #save_urls('URL_LIST2.csv', sorted(LISTURL))
    save_urls('URL_LIST2.csv', LISTURL)
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
    url1 = fetch0()
    #url2 = fetch()
    #fetch2(url2)