import socket
import ssl
import threading

HOST = '0.0.0.0'
PORT = 9999

clients = {}


def broadcast(message, sender_socket=None):
    # (Bu kısım aynı, değişmedi)
    dead_clients = []
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                dead_clients.append(client)
    for dc in dead_clients:
        if dc in clients:
            del clients[dc]


def handle_client(client_socket, addr):
    # (Bu kısım aynı, değişmedi)
    print(f"[+] Yeni bağlantı: {addr}")
    try:
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        print(f"[+] {username} giriş yaptı.")
        broadcast(f"👋 {username} katıldı!")

        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg: break
            full_msg = f"{username}: {msg}"
            print(f"[Chat] {full_msg}")
            broadcast(full_msg, sender_socket=client_socket)

    except Exception as e:
        print(f"[-] Hata ({addr}): {e}")
    finally:
        # Güvenli silme işlemi (pop kullanıyoruz)
        username = clients.pop(client_socket, None)
        if username:
            print(f"[-] {username} ayrıldı.")
            broadcast(f"🚪 {username} ayrıldı.")
        client_socket.close()


def main():
    # 1. SSL Hazırlığı
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    # 2. HAM (RAW) TCP SOKET OLUŞTUR
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"--- 🛡️ GÜÇLENDİRİLMİŞ SERVER ({PORT}) ---")
    print("Ngrok ve Local bağlantılar bekleniyor...")

    while True:
        try:
            # 3. ÖNCE BAĞLANTIYI KABUL ET (Şifresiz)
            # Burası artık hata vermez çünkü standart TCP kabul ediyoruz.
            raw_sock, addr = server.accept()

            # 4. ŞİMDİ SSL GİYDİR (Wrap Socket)
            # Hatayı burada yakalayacağız ki sunucu çökmesin.
            try:
                ssl_sock = context.wrap_socket(raw_sock, server_side=True)

                # Başarılıysa Thread başlat
                threading.Thread(target=handle_client, args=(ssl_sock, addr), daemon=True).start()

            except ssl.SSLError as e:
                print(f"⚠️ SSL Hatası (Biri yanlış bağlandı): {e}")
                raw_sock.close()  # Hatalı bağlantıyı kapat

        except Exception as e:
            print(f"⚠️ Sunucu Hatası: {e}")


if __name__ == "__main__":
    main()