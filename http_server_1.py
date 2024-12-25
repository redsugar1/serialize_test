import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# 自訂的請求處理器
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Temporary HTTP server is running!")

# 啟動伺服器的函數
def run_server():
    server_address = ('', 8887)
    httpd = HTTPServer(server_address, SimpleHandler)
    print("Server running on port 8887...")
    
    # 儲存伺服器實例，方便之後關閉
    global server_instance
    server_instance = httpd
    
    httpd.serve_forever()

# 啟動伺服器執行緒
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True  # 設置為守護執行緒
server_thread.start()

# 模擬一些其他操作
import time
time.sleep(10)  # 伺服器運行 10 秒

# 關閉伺服器
print("Shutting down server...")
server_instance.shutdown()  # 停止伺服器
server_instance.server_close()  # 關閉伺服器


