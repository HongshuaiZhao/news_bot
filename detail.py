import os
import requests
from bs4 import BeautifulSoup
import hashlib

NEWS_DATA_DIR = 'news_data'


def fetch_content_and_images(folder_path, link_url):
    response = requests.get(link_url)
    if response.status_code != 200:
        print(f'Failed to retrieve {link_url}')
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.find('div', class_='index_cententWrap__Jv8jK')
    if not content_div:
        print(f'No content div found in {link_url}')
        return

    paragraphs = content_div.find_all('p')
    with open(os.path.join(folder_path, 'content.txt'), 'w', encoding='utf-8') as f:
        for p in paragraphs:
            f.write(p.get_text() + '\n\n')

    images = content_div.find_all('img')
    for img in images:
        img_url = img.get('src')
        if img_url:
            img_url = requests.compat.urljoin(link_url, img_url)
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                md5_hash = hashlib.md5(img_url.encode()).hexdigest()
                img_path = os.path.join(folder_path, f'image_{md5_hash}.jpg')
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)


for channel_name in os.listdir(NEWS_DATA_DIR):
    channel_path = os.path.join(NEWS_DATA_DIR, channel_name)
    if os.path.isdir(channel_path):
        for folder_name in os.listdir(channel_path):
            folder_path = os.path.join(channel_path, folder_name)
            if os.path.isdir(folder_path):
                link_file = os.path.join(folder_path, 'link.txt')
                if os.path.exists(link_file):
                    with open(link_file, 'r', encoding='utf-8') as f:
                        link_url = f.read().strip()
                        fetch_content_and_images(folder_path, link_url)
                else:
                    print(f'No link.txt in {folder_path}')