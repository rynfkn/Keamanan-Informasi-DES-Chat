import socket
import threading
import base64
import json
from DES import encrypt_text, decrypt_text
import sys

class Client:
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        self.server_socket = None
        self.key = None
        self.running = False
        
    def connect(self, key):
        if len(key) != 8:
            print(f"[!] WARNING: KEY MUST BE 8 CHARACTER")
            return False
        
        self.key = key.encode('utf-8')

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            key_data = json.dumps({
                'key': key
            })
            self.client_socket.send(key_data.encode('utf-8'))

            print("="*25)
            print(f"CONNECTED TO SERVER {self.host}:{self.port}")
            print("="*25 + "\n")

            self.running = True

            receive_thread = threading.Thread(
                target=self.receive_message
            )
            receive_thread.daemon = True
            receive_thread.start()

            return True
        except Exception as e:
            print(f"[!] FAILED CONNECTING TO SERVER: {e}")
            return False
    
    def receive_message(self):
        while self.running:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break

                message_data = json.loads(data.decode('utf-8'))

                if message_data.get('type') == 'system':
                    print(f"\n[SYSTEM] {message_data.get('message')}\n> ", end='', flush=True)
                    continue
                
                else:
                    encrypted_text = message_data.get('encrypted_text', '')
                    sender_key = message_data.get('sender_key', '')

                    decrypted = decrypt_text(encrypted_text, self.key)
                    print(f"[ENCRYPTED MESSAGE]: {encrypted_text}")
                    print(f"[DECRYPTED MESSAGE]: {decrypted}")
                    print("> ", end='', flush=True)

            except Exception as e:
                if self.running:
                    print(f"[!] ERROR RECEIVING MESSAGE: {e}")
                break

        print("[!] LOST CONNECTION TO SERVER")
    
    def send_message(self, plaintext):
        try:
            encrypted = encrypt_text(plaintext, self.key)
            message_data = {
                'type': 'message',
                'encrypted_text': encrypted,
                'sender_key': self.key.decode('utf-8')
            }

            message_json = json.dumps(message_data)
            self.client_socket.send(message_json.encode('utf-8'))

        except Exception as e:
            print(f"[!] FAILED SENDING MESSAGE")

    def start_chat(self):
        try:
            while self.running:
                message = input("> ")
                
                if message.lower() in ['quit', 'exit']:
                    print(f"[*] QUITING THE CHAT")
                    break
                
                if message.strip():
                    self.send_message(message)
        except KeyboardInterrupt:
            print(f"[*] CHAT STOPPED")
        finally:
            self.disconnect()

    def disconnect(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()


def main():
    print("=====================================")
    print("     DES CHAT CLIENT INTERFACE     ")
    print("=====================================")

    input_host = input("ENTER HOST (default=127.0.0.1) >> ") or "127.0.0.1"
    input_port = input("ENTER PORT (default=1234) >> ") or "1234"

    try:
        port_num = int(input_port)
        if not (0 < port_num < 65536):
            raise ValueError("Invalid port range")
    except ValueError:
        print("[!] INVALID PORT. MUST BE A NUMBER BETWEEN 1–65535.")
        sys.exit(1)

    key = input("Enter key (8 Character): ").strip()

    if len(key) != 8:
        print("[!] WARNING: KEY MUST BE 8 CHARACTER")
        return
    
    client = Client(host=input_host, port=port_num)
    
    if client.connect(key):
        client.start_chat()

if __name__ == '__main__':
    main()