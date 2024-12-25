
import subprocess
import time

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

# 啟動伺服器
server_process = start_http_server(port=8080, directory=".")

# 等待 10 秒
time.sleep(10)

# 關閉伺服器
stop_http_server(server_process)

