import socket
import threading   
import hashlib 
import base64

class Server:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('', 12000)) # automatically find open port to connect to
        self._socket.listen()
        print("receiver active on", socket.gethostbyname(socket.gethostname()), "port", self._socket.getsockname()[1])
        while True:
            conn, addr = self._socket.accept()
            print("connected by", addr)
            thread = threading.Thread(target=self.run_thread, args=[conn])
            thread.start()
            # serve connection
            # Implement this
            
            # Single thread placeholder to echo raw bytes
 
    def __del__(self):
        self._socket.close()

    def run_thread(self, conn):
        data = conn.recv(1024)
        string_data = data.decode('ascii')
        string_data_array = string_data.split('\r\n')
        if self.is_handshake(string_data_array):
            print("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + self.sec_websocket_accept(string_data_array))
            conn.sendall("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + self.sec_websocket_accept(string_data_array))
        while True:
            data = conn.recv(1024)
            print(data)
            if not data:
                break
            conn.sendall(data)  

    def is_handshake(self, string_data_array):
        return string_data_array[2] == "Upgrade: websocket" and string_data_array[3] == "Connection: Upgrade" and string_data_array[5] == "Sec-WebSocket-Version: 13"

    def sec_websocket_accept(self, string_data_array):
        websocket_key = string_data_array[4].split(' ')[1]
        return base64.b64encode(hashlib.sha1((websocket_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()))

if __name__ == "__main__":
    r = Server()