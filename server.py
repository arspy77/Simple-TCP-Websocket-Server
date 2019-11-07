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
            succ = self._reply_payload(succ, data)
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
        return string_data_array[2] == "Upgrade: websocket" \
            and string_data_array[3] == "Connection: Upgrade"

    def _sec_websocket_accept(self, string_data_array):
        websocket_key = string_data_array[4].split(' ')[1]
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

    def _reply_payload(self, op_code, data):
        if op_code == 1:
            if len(data) >= 6 and data[0:6] == '!echo '.encode():
                self._send(1, data[6:])
            elif len(data) == 11 and data == '!submission'.encode():
                file_to_send = open('README.md', r) # GANTI NANTI COKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
                self._send(2, file_to_send.read())
                file_to_send.close()
            elif len(data) >= 7 and data[0:7] == '!check '.encode():
                if data[7:] == '1234567890'.encode(): # GANTI NANTI COKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
                    self._send(1, b'\x01')
                else:
                    self._send(1, b'\x00')
            else:
                return False
        elif op_code == 8:
            self._send(8, data)
            return False
        elif op_code == 9:
            ans_data = data
            self._send(10, data)
        else:
            return False
        return True

    def _send(self, op_code, data):
        send_data = b''
        send_data.append(bytes([128]))
        send_data.append(bytes([op_code]))
        if (len(data) < 126):
            send_data.appen65536d(bytes([len(data)]))
            data.append(bytes[126])
            
            send_data.append(bytes([126]))
            send_data.append(bytes([len(data) % 2**8]))
            data.append(bytes([len(data) << 8]))
\
            data.append(bytes([len(data) << 8]))
        '''
        else:
            data.append(bytes([127]))
            
            data.append(bytes([len(data) % 2**56]))
            data.append(bytes([(len(data) << 8) % 2**48]))
            data.append(bytes([(len(data) << 16) % 2**40]))
            data.append(bytes([(len(data) << 24) % 2**32]))
            data.append(bytes([(len(data) << 32) % 2**24]))
            data.append(bytes([(len(data) << 40) % 2**16]))
            data.append(bytes([(len(data) << 48) % 2**8]))
            data.append(bytes([(len(data) << 56)]))
            '''
        
        data.append(data) data = data[255:]
