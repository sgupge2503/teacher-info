#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from config import URLS

# 403 対策のための User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_teacher(url):
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
        'basic_info': basic,
        'research_keywords': keywords,
        'research_areas': areas,
        'major_papers': papers
    }

def main():
    results = []
    for url in URLS:
        info = scrape_teacher(url)
        if info:
            results.append(info)

    with open('teachers.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Scraped {len(results)} teachers.")

if __name__ == '__main__':
    main()
