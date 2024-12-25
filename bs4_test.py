import requests
from bs4 import BeautifulSoup

url = 'http://192.168.139.129/shop/dashboard/?page=products.php'
cookies ={
    'PHPSESSID': 'djbtdkut12o62990vctlbebmo1'
}
resp = requests.get(url, cookies=cookies)
#print(resp)
soup = BeautifulSoup(resp.text, 'html.parser')
print(soup)

# 查找所有匹配的 <a> 標籤
all_links = soup.find_all('a', class_='btn btn-info btn-sm')

# 確保有結果，並提取最後一個
if all_links:
    last_link = all_links[-1]  # 取最後一個
    href = last_link.get('href')
    print("最後一個連結：", href)
    if href and "id=" in href:
        # 解析 id 值
        id_value = href.split("id=")[-1]  # 提取 id 後的內容
        print("提取的 id 值：", id_value)
else:
    print("未找到指定的標籤")
