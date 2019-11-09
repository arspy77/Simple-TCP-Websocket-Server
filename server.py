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
        i = 1
        while True:
            conn, addr = self._socket.accept()
            print("connected by", addr, " on thread ", i)
            thread = threading.Thread(target=self._run_thread, args=[conn, i])
            thread.start()
            i += 1
 
    def __del__(self):
        self._socket.close()

    def _run_thread(self, conn, n):
        data = conn.recv(1024)
        succ, ans = self._reply_handshake(data)
        if not succ:
            print("handshake failed on thread ", n)
            return
        conn.sendall(ans)
        print("handshake succeeded on thread ", n)
        while True:
            succ, data = self._receive_payload(conn)
            if not succ:
                print("connection closed on thread ", n)
                conn.close()
                return 
            succ = self._reply_payload(succ, data, conn, n)
            if not succ:
                print("connection closed on thread ", n)
                conn.close()
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
                data = conn.recv(8)
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

    def _reply_payload(self, op_code, data, conn, n):
        if op_code == 1:
            if len(data) >= 6 and data[0:6] == '!echo '.encode():
                print(data.decode('ascii'), "on thread ", n)
                self._send(1, data[6:].decode('ascii').encode('utf-8'), conn)
            elif len(data) == 11 and data == '!submission'.encode():
                print('submission on thread ', n)
                file_to_send = open('Jarkom2_KomiCantNetwork.zip', "rb") 
                self._send(2, file_to_send.read(), conn)
                file_to_send.close()
            elif len(data) >= 7 and data[0:7] == '!check '.encode():
                print(data.decode('ascii'), "on thread ", n)
                file_to_send = open('Jarkom2_KomiCantNetwork.zip', "rb") 
                if data[7:].decode('ascii').lower() == hashlib.md5(file_to_send.read()).hexdigest().lower(): 
                    print("checksum succeeded on thread ", n)
                    self._send(1, bytes([ord('1')]).decode('ascii').encode('utf-8'), conn)
                else:
                    print("checksum failed on thread ", n)
                    self._send(1, bytes([ord('0')]).decode('ascii').encode('utf-8'), conn)
                file_to_send.close()
            else:
                return False
        elif op_code == 8:
            print("close control frame received on thread ", n)
            self._send(8, data, conn)
            return False
        elif op_code == 9:
            print("ping received on thread ", n)
            self._send(10, data, conn)
        else:
            return False
        return True

    def _send(self, op_code, data, conn):
        is_first = True
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
                send_data += (bytes([packet_length >> 8]))
                send_data += (bytes([packet_length & 0xFF]))
            packet_data = data[:packet_length]
            send_data += (packet_data) 
            conn.sendall(send_data)
            data = data[packet_length:]


server = Server()