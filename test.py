import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

urls = [
    'https://www.thepaper.cn/channel_143064',
    'https://www.thepaper.cn/channel_128409',
    'https://www.thepaper.cn/channel_25950',
    'https://www.thepaper.cn/channel_122908',
    'https://www.thepaper.cn/channel_25951',
    'https://www.thepaper.cn/channel_119908',
]

NEWS_DATA_DIR = 'news_data'


def sanitize_filename(filename):
    return ''.join([c for c in filename if c.isalnum() or c in [' ', '_', '-']]).strip()


for url in urls:
    channel_name = url.split('/')[-1]
    channel_dir = os.path.join(NEWS_DATA_DIR, channel_name)
    if not os.path.exists(channel_dir):
        os.makedirs(channel_dir)

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    news_cards = soup.find_all('div',
                               class_='ant-card ant-card-bordered ant-card-hoverable small_basecard__tH4iV small_article_card__xBP8q')

    for index, card in enumerate(news_cards):
        title_tag = card.find('h2')
        if not title_tag:
            continue
        title = title_tag.get_text()
        folder_name = f"{index:03d}_{sanitize_filename(title[:50])}"
        folder_path = os.path.join(channel_dir, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        img_tag = card.find('img')
        if img_tag:
            img_url = urljoin(url, img_tag.get('src', ''))
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open(os.path.join(folder_path, 'main_image.jpg'), 'wb') as f:
                    f.write(img_response.content)

        with open(os.path.join(folder_path, 'title.txt'), 'w', encoding='utf-8') as f:
            f.write(title)

        a_tag = card.find('a', target='_blank')
        if a_tag:
            jump_url = urljoin(url, a_tag.get('href', ''))
            with open(os.path.join(folder_path, 'link.txt'), 'w', encoding='utf-8') as f:
                f.write(jump_url)
        else:
            print(f'No jump link found for {folder_name}')