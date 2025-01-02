import os
import requests
from bs4 import BeautifulSoup
import hashlib

base_dir = 'news_data'

for folder_name in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.isdir(folder_path):
        link_file = os.path.join(folder_path, 'link.txt')
        if os.path.exists(link_file):
            try:
                with open(link_file, 'r', encoding='utf-8') as f:
                    link_url = f.read().strip()
                    response = requests.get(link_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        content_div = soup.find('div', class_='index_cententWrap__Jv8jK')
                        if content_div:
                            # 提取所有<p>和<img>标签
                            paragraphs = content_div.find_all('p')
                            images = content_div.find_all('img')
                            # 保存文字内容到content.txt
                            with open(os.path.join(folder_path, 'content.txt'), 'w', encoding='utf-8') as content_f:
                                for p in paragraphs:
                                    content_f.write(p.get_text() + '\n\n')
                            # 下载图片并保存
                            for img in images:
                                img_url = img.get('src')
                                if img_url:
                                    # 处理相对路径
                                    img_url = requests.compat.urljoin(link_url, img_url)
                                    img_response = requests.get(img_url)
                                    if img_response.status_code == 200:
                                        # 生成唯一的文件名，比如用md5
                                        md5_hash = hashlib.md5(img_url.encode()).hexdigest()
                                        img_path = os.path.join(folder_path, f'image_{md5_hash}.jpg')
                                        with open(img_path, 'wb') as img_f:
                                            img_f.write(img_response.content)
                        else:
                            print(f'No content div found in {link_url}')
                    else:
                        print(f'Failed to retrieve {link_url}')
            except Exception as e:
                print(f'Error processing {folder_path}: {e}')
        else:
            print(f'No link.txt in {folder_path}')
    else:
        print(f'{folder_path} is not a directory')