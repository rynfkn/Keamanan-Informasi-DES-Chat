import socket
import threading
import base64
import json
from DES import encrypt_text, decrypt_text

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

            self.running = True

            receive_thread = threading.Thread(
                target=self.receive_message
            )
            receive_thread.daemon = True
            receive_thread.start()

            return True
        except Exception as e:
            print(f"FAILED CONNECTING TO SERVER: {e}")
            return False
    
    def receive_message(self):
        while self.running:
            try:
                data = self.client_socket.recv(4096)
                message_data = json.loads(data.decode('utf-8'))

                if message_data.get('type') == 'system':
                    print(f"\n[SISTEM] {message_data.get('message')}\n> ", end='', flush=True)
                
                else:
                    encrypted_text = message_data.get('encrypted_text', '')
                    sender_key = message_data.get('sender_key', '')

                    try:
                        decrypted_text = decrypt_text(encrypted_text, self.key)
                        print("[KEY IS MATCH]")
                        print(f"ENCRYPTED MESSAGE: {encrypted_text}")
                        print(f"DECRYPTED MESSAGE: {decrypted_text}")
                        print("> ", end='', flush=True)

                    except:
                        print(f"[KEY DOESN'T MATCH]")
                        print(f"ENCRYPTED MESSAGE: {encrypted_text}")
                        print("> ", end='', flush=True)

            except Exception as e:
                if self.running:
                    print(f"ERROR RECEIVING MESSAGE: {e}")
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
                    print(f"QUITING THE CHAT")
                    break
                
                if message.strip():
                    self.send_message(message)
        except KeyboardInterrupt:
            print(f"CHAT STOPPED")
        finally:
            self.disconnect()

    def disconnect(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()


def main():
    print("=" * 50)
    print("  DES Encrypted Chat Client")
    print("=" * 50)
    print()

    key = input("Enter key (8 Character): ").strip()

    if len(key) != 8:
        print("[!] WARNING: KEY MUST BE 8 CHARACTER")
        return

    client = Client()
    
    if client.connect(key):
        client.start_chat()

if __name__ == '__main__':
    main()