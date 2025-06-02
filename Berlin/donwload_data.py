#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-06-01 11:10 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : donwload_data.py
# @IDE     : PyCharm
# ---------------------------------------------------
import xml.etree.ElementTree as ET
import feedparser
import requests
import os

# 你的 feed 地址（柏林 LoD2 模型入口）
feed_url = "https://fbinter.stadt-berlin.de/fb/feed/senstadt/a_lod2/0"

# 输出路径
save_dir = "G:\BuildingWorld\Europe\Berlin\data"
os.makedirs(save_dir, exist_ok=True)

# 解析 Atom Feed
feed = feedparser.parse(feed_url)

zip_links = []
for entry in feed.entries:
    for link in entry.links:
        if link.get("href", "").endswith(".zip"):
            zip_links.append(link["href"])

print(len(zip_links))

for url in zip_links:
    filename = os.path.basename(url)
    file_path = os.path.join(save_dir, filename)

    if os.path.exists(file_path):
        print(f"✅ 已存在：{filename}")
        continue

    try:
        print(f"⬇️ 正在下载：{filename}")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ 完成：{filename}\n")
    except Exception as e:
        print(f"❌ 下载失败：{filename}，原因：{e}\n")