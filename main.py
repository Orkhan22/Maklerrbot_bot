import requests
from bs4 import BeautifulSoup
import os

# Ayarlar
TOKEN = "8666608099:AAFhdnrexdxUkfIeCpK_6zq1NdTEdQAVFKQ"
CHAT_ID = "644928091"
URL = "https://bina.az/baki/alqi-satqi/menziller/kohne-tikili?rooms[]=3&repair[]=1" # Filtrlənmiş link

def check_bina():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Elanları tapırıq
    items = soup.find_all('div', class_='items-list-item')
    
    # Əvvəlki tapılan elanları oxuyuruq
    if os.path.exists("seen_ids.txt"):
        with open("seen_ids.txt", "r") as f:
            seen_ids = f.read().splitlines()
    else:
        seen_ids = []

    new_ids = []
    for item in items:
        link_tag = item.find('a', class_='item_link')
        if link_tag:
            full_link = "https://bina.az" + link_tag['href']
            listing_id = link_tag['href'].split('/')[-1]
            
            if listing_id not in seen_ids:
                # Yeni elan tapıldı! Telegram-a göndər
                message = f"Yeni mənzil! 🏠\nQiymət: {item.find('span', class_='price-val').text}\nLink: {full_link}"
                requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}")
                new_ids.append(listing_id)

    # Yeni ID-ləri fayla yazırıq
    with open("seen_ids.txt", "a") as f:
        for nid in new_ids:
            f.write(nid + "\n")

check_bina()
