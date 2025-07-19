#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from config import URLS

# 403 対策のための User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def download_image(image_url, save_path):
    """画像をダウンロードして保存する"""
    try:
        resp = requests.get(image_url, headers=HEADERS)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return True
        else:
            print(f"Failed to download image from {image_url}: HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading image from {image_url}: {e}")
        return False

def scrape_teacher(url, image_counter):
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Skipped {url}: HTTP {resp.status_code}")
        return None

    soup = BeautifulSoup(resp.content, 'html.parser')

    # 教員名とルビ
    name_tag = soup.find('h1', class_='rm-researcher-name')
    ruby_tag = soup.find('div', class_='rm-ruby')
    name = name_tag.get_text(strip=True) if name_tag else None
    ruby = ruby_tag.get_text(strip=True) if ruby_tag else None

    # プロフィール画像
    image_path = ""
    page_header = soup.find('div', class_='rm-page-header')
    if page_header:
        # rm-page-header内のrm-avatarクラス内の画像を探す
        avatar_div = page_header.find('div', class_='rm-avatar')
        if avatar_div:
            img_tag = avatar_div.find('img')
            if img_tag and img_tag.get('src'):
                image_url = urljoin(url, img_tag['src'])
                # 拡張子を取得
                parsed_url = urlparse(image_url)
                original_filename = os.path.basename(parsed_url.path)
                extension = os.path.splitext(original_filename)[1] if '.' in original_filename else '.jpg'
                
                # 連番でファイル名を生成
                filename = f"image{image_counter:02d}{extension}"
                
                # 画像を保存
                save_path = os.path.join('images', filename)
                if download_image(image_url, save_path):
                    image_path = save_path
                    print(f"Downloaded image: {image_path}")
                else:
                    print(f"Failed to download image for {name}")
            else:
                print(f"No image found for {name}")
        else:
            print(f"No avatar div found for {name}")

    # 基本情報
    basic = {}
    profile = soup.find(id='profile')
    if profile:
        panel = profile.find_parent('div', class_='panel')
        body = panel.find('div', class_='panel-body')
        for dl in body.find_all('dl', class_='rm-cv-basic-dl'):
            dt = dl.find('dt').get_text(strip=True)
            dd = dl.find('dd').get_text(" ", strip=True)
            basic[dt] = ' '.join(dd.split())

    # 研究キーワード
    keywords = [
        a.get_text(strip=True)
        for a in soup.select('.research_interests-body .rm-cv-list-title')
    ]

    # 研究分野
    areas = [
        a.get_text(strip=True)
        for a in soup.select('.research_areas-body .rm-cv-list-title')
    ]

    # 主要な論文（タイトル＋リンク）
    papers = []
    for a in soup.select('.published_papers-body .rm-cv-list-title'):
        title = a.get_text(strip=True)
        link  = urljoin(url, a['href'])
        papers.append({'title': title, 'link': link})

    return {
        'url': url,
        'name': name,
        'ruby': ruby,
        'image': image_path,
        'basic_info': basic,
        'research_keywords': keywords,
        'research_areas': areas,
        'major_papers': papers
    }

def main():
    results = []
    image_counter = 1
    for url in URLS:
        info = scrape_teacher(url, image_counter)
        if info:
            results.append(info)
            # 画像が正常にダウンロードされた場合のみカウンターを増加
            if info.get('image'):
                image_counter += 1

    with open('teachers.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Scraped {len(results)} teachers.")

if __name__ == '__main__':
    main()
