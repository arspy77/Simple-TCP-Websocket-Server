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
            thread = threading.Thread(target=self._run_thread, args=[conn])
            thread.start()
            # serve connection
            # Implement this
            
            # Single thread placeholder to echo raw bytes
 
    def __del__(self):
        self._socket.close()

    def _run_thread(self, conn):
        data = conn.recv(1024)
        print(data)
        succ, ans = self._reply_handshake(data)
        print(ans)
        if not succ:
            return
        conn.sendall(ans)
        while True:
            succ, data = self._receive_payload(conn)
            if not succ:
                return 
            print(data)
            succ = self._reply_payload(succ, data, conn)
            if not succ:
                return


    def _reply_handshake(self, data):
        string_data = data.decode('ascii')
        string_data_array = string_data.split('\r\n')
        if self._is_handshake(string_data_array):
            send_string = \
                "HTTP/1.1 101 Switching Protocols\r\n"\
                + "Upgrade: websocket\r\n" \
                + "Connection: Upgrade\r\n" \
                + "Sec-WebSocket-Accept: " \
                + self._sec_websocket_accept(string_data_array).decode('ascii') \
                + "\r\n\r\n"
            x = send_string.encode()
            print(x)
            return True, x
        return False, None

    def _is_handshake(self, string_data_array):
        return "Upgrade: websocket" in string_data_array \
        and "Connection: Upgrade" in string_data_array

    def _sec_websocket_accept(self, string_data_array):
        websocket_key = ''
        for i in range(len(string_data_array)):
            if string_data_array[i].split(' ')[0] == "Sec-WebSocket-Key:":
                websocket_key = string_data_array[i].split(' ')[1]
        return base64.b64encode(hashlib.sha1((websocket_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())

    def _receive_payload(self, conn):
        ans = b''
        is_first = True
        while True:
            # 4294967295
            data = conn.recv(2)
            if len(data) < 2:
                return 0, None
            is_fin = data[0] >> 7
            if is_first:
                op_code = data[0] & 0x0F
            is_first = False
            if (op_code == 9):
                data = conn.recv(2)
                return op_code, conn.recv(1024)
            is_mask = data[1] >> 7
            payload_length = data[1] & 0x7F 
            if payload_length == 126:
                data = conn.recv(2)
                if len(data) < 2:
                    return 0, None
                payload_length = int.from_bytes(data, 'big')
            elif payload_length == 127:
                data = con.recv(8)
                if len(data) < 8:
                    return 0, None
                payload_length = int.from_bytes(data, 'big')
            if is_mask != 0:
                mask = conn.recv(4)
                if len(mask) < 4:
                    return 0, None
            for i in range(payload_length):
                data = conn.recv(1)
                if len(data) < 1:
                    return 0, None
                if is_mask:
                    ans += bytes([data[0] ^ mask[i % 4]])
                else:
                    ans += data[0]
            if is_fin:
                break

        return op_code, ans

    def _reply_payload(self, op_code, data, conn):
        if op_code == 1:
            if len(data) >= 6 and data[0:6] == '!echo '.encode():
                self._send(1, data[6:], conn)
            elif len(data) == 11 and data == '!submission'.encode():
                file_to_send = open('Jarkom2_KomiCantNetwork.zip', "rb") 
                self._send(2, file_to_send.read(), conn)
                file_to_send.close()
            elif len(data) >= 7 and data[0:7] == '!check '.encode():
                file_to_send = open('Jarkom2_KomiCantNetwork.zip', "rb") 
                if data[7:].decode('ascii').lower() == hashlib.md5(file_to_send.read()).hexdigest().lower(): 
                    self._send(1, bytes([ord('1')]), conn)
                else:
                    self._send(1, bytes([ord('0')]), conn)
                file_to_send.close()
            else:
                return False
        elif op_code == 8:
            print("close control frame received")
            self._send(8, data, conn)
            return False
        elif op_code == 9:
            print("ping received")
            self._send(10, data, conn)
        else:
            return False
        return True

    def _send(self, op_code, data, conn):
        is_first = True
        print(data)
        while len(data) > 0: 
            send_data = b''
            if (len(data) <= 32768):
                if is_first:
                    send_data += (bytes([128 + op_code]))
                    is_first = False
                else:
                    send_data += (bytes([128]))
            else:
                if is_first:
                    send_data += (bytes([op_code]))
                    is_first = False
                else:
                    send_data += (bytes([0]))
            packet_length = min(32768, len(data))
            if (packet_length < 126):
                send_data += (bytes([packet_length]))
            else:    
                send_data += (bytes([126]))
                send_data += (bytes([packet_length % 2**8]))
                send_data += (bytes([((packet_length << 8) % 2**8)]))
            packet_data = data[:packet_length]
            send_data += (packet_data) 
            print(send_data)
            conn.sendall(send_data)
            data = data[packet_length:]


server = Server()