import socket
import threading   
import hashlib 
import base64

class Server:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('localhost', 12000))
        self._socket.listen()
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
            succ, data = self._receive_payload(conn, n)
            if not succ:
                self._send_close(conn, n)
                print("connection closed not normally on thread ", n)
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

    def _receive_payload(self, conn, n):
        ans = b''
        is_first = True
        while True:
            diff = 0
            data = conn.recv(65536)
            if len(data) < 2:
                print("error data length < 2 on thread ", n)
                return 0, None
            is_fin = data[0] >> 7
            if is_first:
                op_code = data[0] & 0x0F
            new_op_code = data[0] & 0x0F 
            is_mask = data[1] >> 7
            payload_length = data[1] & 0x7F
            if (not(is_first)) and (new_op_code != 0):
                if new_op_code == 8 or new_op_code == 9 or new_op_code == 10:
                    print("control frame in between data frames on thread ", n)
                    not_closed = self._receive_payload_control(conn, op_code, is_mask, payload_length, n, data, diff)
                    if not(not_closed):
                        return 0, None
                else:
                    print("unknown control frame on thread ", n)
                continue
            is_first = False
            if payload_length == 126:
                if len(data) < 4:
                    print("error data length < 4 on thread ", n)
                    return 0, None
                payload_length = int.from_bytes(data[2:4], 'big')
                diff += 2
            elif payload_length == 127:
                if len(data) < 10:
                    print("error data length < 10 on thread ", n)
                    return 0, None
                payload_length = int.from_bytes(data[2:10], 'big')
                diff += 8
            if is_mask != 0:
                mask = data[2+diff:6+diff]
                if len(mask) < 4:
                    print("error mask length < 4 on thread ", n)
                    return 0, None
                diff += 4
            for i in range(2+diff, len(data)):
                if is_mask:
                    ans += bytes([data[i] ^ mask[(i-2-diff) % 4]])
                else:
                    ans += data[i]
            if is_fin:
                break
        return op_code, ans

    def _receive_payload_control(self, conn, op_code, is_mask, payload_length, n, data, diff):
        if payload_length == 126:
            payload_length = int.from_bytes(data[2:4], 'big')
            diff += 2
        elif payload_length == 127:
            payload_length = int.from_bytes(data[2:10], 'big')
            diff += 8
        if is_mask != 0:
            mask = data[2+diff:6+diff]
        for i in range(2+diff, payload_length+2+diff):
            if is_mask:
                ans += bytes([data[i] ^ mask[(i-2-diff) % 4]])
            else:
                ans += data[i]
        return self._reply_payload(op_code, ans, conn, n)

    def _reply_payload(self, op_code, data, conn, n):
        global zip_contents
        global md5_hash
        if op_code == 1:
            if len(data) >= 6 and data[0:6] == '!echo '.encode():
                print(data.decode('ascii'), "on thread ", n)
                self._send(1, data[6:].decode('ascii').encode('utf-8'), conn)
            elif len(data) == 11 and data == '!submission'.encode():
                print('submission on thread ', n)
                self._send(2, zip_contents, conn)
            else:
                print("unknown text payload on thread", n)
        elif op_code == 2:
            print("binary payload on thread", n)
            if hashlib.md5(data).hexdigest().lower() == md5_hash: 
                print("md5 checksum succeeded on thread ", n)
                self._send(1, bytes([ord('1')]).decode('ascii').encode('utf-8'), conn)
            else:
                print("md5 checksum failed on thread ", n)
                self._send(1, bytes([ord('0')]).decode('ascii').encode('utf-8'), conn)
        elif op_code == 8:
            print("close control frame received on thread ", n)
            self._send(8, data, conn)
            return False
        elif op_code == 9:
            print("ping received on thread ", n)
            self._send(10, data, conn)
        elif op_code == 10:
            print("pong received on thread ", n)
        else:
            print("unknown frame on thread ", n)
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
    
    def _send_close(self, conn, n):
        print("close control frame sent on thread ", n)
        self._send(8, bytes([ord('0')]), conn)

global zip_contents
global md5_hash
file_to_send = open('Jarkom2_KomiCantNetwork.zip', "rb") 
zip_contents = file_to_send.read()
file_to_send.close()
md5_hash =  hashlib.md5(zip_contents).hexdigest().lower()
server = Server()