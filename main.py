import requests
from bs4 import BeautifulSoup
import os

# Ayarlar
TOKEN = "8666608099:AAFhdnrexdxUkfIeCpK_6zq1NdTEdQAVFKQ"
CHAT_ID = "644928091"
URL = "https://bina.az/baki/alqi-satqi/menziller/kohne-tikili?rooms[]=3&repair[]=1"

def check_bina():
    # Sayta "insan" olduğumuzu bildirmək üçün headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Elanları tapırıq (Bina.az-ın həm köhnə, həm yeni klasslarını yoxlayırıq)
        items = soup.find_all('div', class_='items-list-item') or soup.find_all('div', class_='items_list-item')
        
        if not items:
            print("Heç bir elan tapılmadı. Sayt strukturu dəyişmiş ola bilər.")
            return

        # Əvvəlki tapılan elanları oxuyuruq
        seen_ids = set()
        if os.path.exists("seen_ids.txt"):
            with open("seen_ids.txt", "r") as f:
                seen_ids = set(f.read().splitlines())

        new_ids = []
        for item in items:
            link_tag = item.find('a')
            if link_tag and 'href' in link_tag.attrs:
                href = link_tag['href']
                # Sırf mənzil linki olduğuna əmin oluruq
                if "/items/" not in href:
                    continue
                    
                listing_id = href.split('/')[-1]
                
                if listing_id not in seen_ids:
                    full_link = "https://bina.az" + href
                    
                    # Qiyməti tapmağa çalışırıq (xəta verməməsi üçün yoxlayırıq)
                    price_tag = item.find('span', class_='price-val')
                    price_text = price_tag.text.strip() if price_tag else "Qiymət yoxdur"
                    
                    curr_tag = item.find('span', class_='price-cur')
                    curr_text = curr_tag.text.strip() if curr_tag else ""

                    message = f"Yeni mənzil! 🏠\nQiymət: {price_text} {curr_text}\nLink: {full_link}"
                    
                    # Telegram-a göndər
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": message})
                    
                    new_ids.append(listing_id)
                    seen_ids.add(listing_id)

        # Yeni ID-ləri fayla əlavə edirik
        if new_ids:
            with open("seen_ids.txt", "a") as f:
                for nid in new_ids:
                    f.write(nid + "\n")
            print(f"{len(new_ids)} yeni elan tapıldı və göndərildi.")
        else:
            print("Yeni elan tapılmadı.")

    except Exception as e:
        print(f"Xəta baş verdi: {e}")

if __name__ == "__main__":
    check_bina()
