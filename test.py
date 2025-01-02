import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import hashlib

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 目标URL
url = 'https://www.thepaper.cn/channel_119908'

# 获取HTML内容
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# 创建主目录
base_dir = 'news_data'
if not os.path.exists(base_dir):
    os.makedirs(base_dir)


# 定义文件名处理函数
def sanitize_filename(filename):
    return ''.join([c for c in filename if c.isalnum() or c in [' ', '_', '-']]).strip()


# 找到所有新闻卡片
news_cards = soup.find_all('div',
                           class_='ant-card ant-card-bordered ant-card-hoverable small_basecard__tH4iV small_article_card__xBP8q')

# 遍历每个新闻卡片
for index, card in enumerate(news_cards):
    # 提取标题
    title_tag = card.find('h2')
    if not title_tag:
        continue  # 跳过没有标题的卡片
    title = title_tag.get_text()

    # 创建文件夹名称，添加编号防止重复
    folder_name = f"{index:03d}_{sanitize_filename(title[:50])}"
    folder_path = os.path.join(base_dir, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 提取图片链接并下载图片
    img_tag = card.find('img')
    if img_tag:
        img_url = urljoin(url, img_tag.get('src', ''))
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            with open(os.path.join(folder_path, 'image.jpg'), 'wb') as f:
                f.write(img_response.content)
        else:
            print(f'Failed to download image from {img_url}')

    # 保存标题到文本文件
    with open(os.path.join(folder_path, 'title.txt'), 'w', encoding='utf-8') as f:
        f.write(title)

    # 提取跳转链接并保存
    a_tag = card.find('a', target='_blank')
    if a_tag:
        jump_url = urljoin(url, a_tag.get('href', ''))
        with open(os.path.join(folder_path, 'link.txt'), 'w', encoding='utf-8') as f:
            f.write(jump_url)
    else:
        print('No jump link found for this card.')

print('Data collection and saving completed.')