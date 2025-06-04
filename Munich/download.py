#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-06-03 10:15 a.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : download.py
# @IDE     : PyCharm
# ---------------------------------------------------
import xml.etree.ElementTree as ET
import requests
from pathlib import Path
import os

# Load and parse the .meta4 XML file
tree = ET.parse(r"E:\BuildingWorld\Munich\data\lod2.meta4")  # Replace with your meta4 file name
root = tree.getroot()

# Define the Metalink XML namespace
ns = {'ml': 'urn:ietf:params:xml:ns:metalink'}

# Iterate over each <file> element
for file_elem in root.findall('ml:file', ns):
    filename = file_elem.get('name')  # Get the file name attribute
    urls = file_elem.findall('ml:url', ns)  # Get all available download URLs
    file_path = os.path.join(r"E:\BuildingWorld\Munich\data", filename)
    print(file_path)

    # Try downloading from each URL until successful
    for url_elem in urls:
        url = url_elem.text
        try:
            print(f"Downloading: {filename} from {url}")
            if os.path.exists(file_path):
                break
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()  # Raise error if HTTP request failed

            # Save the downloaded content to a file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Download successful: {filename}")
            break  # Exit loop if download was successful
        except Exception as e:
            print(f"Download failed: {url}, trying next URL... Error: {e}")
