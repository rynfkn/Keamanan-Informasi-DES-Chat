import socket
import threading
import json

class Server:
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        self.clients = []
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.server_socket.settimeout(1.0)

        print(f"SERVER IS RUNNING IN {self.host}:{self.port}")
        print(f"WAITING FOR CLIENT TO CONNECT")

        try:
            while True:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"[+] NEW CONNECTION FROM: {address}")

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            print("SERVER IS OFF")
        finally:
            for client_socket, _, _ in self.clients:
                client_socket.close()

            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket, address):
        try:
            key_data = client_socket.recv(1024).decode('utf-8')
            client_key = json.loads(key_data).get('key', '')

            self.clients.append((client_socket, address, client_key))
            print(f"[+] CLIENT REGISTERED")

            self.broadcast_message({
                'type': 'system',
                'message': f'NEW CLIENT JOINING: {address}'
            }, exclude_socket=client_socket)

            while True:
                data = client_socket.recv(4096)
                message_data = json.loads(data.decode('utf-8'))

                self.broadcast_message(message_data, exclude_socket=client_socket)

        except Exception as e:
            print(f"ERROR CLIENT {client_socket}: {e}")
        
    def broadcast_message(self, message_data, exclude_socket=None):
        disconnected = []
        for client_socket, address, key in self.clients:
            if client_socket != exclude_socket:
                try:
                    message_json = json.dumps(message_data)
                    client_socket.send(message_json.encode('utf-8'))
                except:
                    disconnected.append(client_socket)
        
        for sock in disconnected:
            self.remove_client(sock)

    def remove_client(self, client_socket):
        self.clients = [
            (sock, addr, key) for sock, addr, key in self.clients 
            if sock != client_socket
        ]
        client_socket.close()

if __name__ == '__main__':
    server = Server()