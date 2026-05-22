import socket
import ssl
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox


class ChatClientGUI:
    def __init__(self):
        # --- GUI AYARLARI ---
        self.root = tk.Tk()
        self.root.title("🔒 Güvenli Sohbet Odası")
        self.root.geometry("600x500")
        self.root.configure(bg="#ecf0f1")

        # --- GİRİŞ BİLGİLERİ ---
        # Program açılınca sorar
        self.target_host = simpledialog.askstring("Bağlantı", "Sunucu IP (veya Ngrok):", parent=self.root)
        self.target_port = simpledialog.askinteger("Bağlantı", "Port Numarası:", parent=self.root)
        self.username = simpledialog.askstring("Giriş", "Kullanıcı Adınız:", parent=self.root)

        if not (self.target_host and self.target_port and self.username):
            self.root.destroy()
            return

        # --- ARAYÜZ TASARIMI ---
        # Başlık
        self.header = tk.Label(self.root, text=f"Bağlı: {self.username} @ {self.target_host}",
                               bg="#2c3e50", fg="white", font=("Arial", 10, "bold"), pady=5)
        self.header.pack(fill=tk.X)

        # Mesaj Okuma Alanı
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled',
                                                   font=("Consolas", 10), bg="white")
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Renk Etiketleri
        self.chat_area.tag_config("me", foreground="blue")  # Benim mesajlarım
        self.chat_area.tag_config("server", foreground="gray", font=("Arial", 9, "italic"))  # Sistem mesajları

        # Mesaj Yazma Alanı
        self.input_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        self.msg_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)  # Enter tuşu ile gönder

        self.send_btn = tk.Button(self.input_frame, text="GÖNDER", command=self.send_message,
                                  bg="#27ae60", fg="white", width=10)
        self.send_btn.pack(side=tk.RIGHT)

        # --- BAĞLANTIYI BAŞLAT ---
        threading.Thread(target=self.connect_to_server, daemon=True).start()

        self.root.mainloop()

    def connect_to_server(self):
        try:
            # SSL Context (Sertifika doğrulamayı kapatıyoruz - Self Signed için)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Socket oluştur ve şifrele
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # SNI göndermiyoruz ki Ngrok kafası karışmasın
            self.client_socket = context.wrap_socket(raw_socket, server_hostname=None)

            self.append_log(f"🔄 {self.target_host}:{self.target_port} sunucusuna bağlanılıyor...", "server")
            self.client_socket.connect((self.target_host, self.target_port))

            # İlk iş ismimizi gönderiyoruz
            self.client_socket.send(self.username.encode('utf-8'))
            self.append_log("✅ Bağlantı Başarılı!", "server")

            # Dinleme fonksiyonunu çalıştır
            self.receive_messages()

        except Exception as e:
            messagebox.showerror("Hata", f"Sunucuya Bağlanılamadı:\n{e}")
            self.root.destroy()

    def receive_messages(self):
        """Sunucudan gelen mesajları sürekli dinleyen döngü"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.append_log(message)
            except:
                self.append_log("⚠️ Bağlantı koptu.", "server")
                self.client_socket.close()
                break

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            try:
                # Mesajı sunucuya yolla
                self.client_socket.send(msg.encode('utf-8'))
                # Kendi ekranımıza da yazalım
                self.append_log(f"Ben: {msg}", "me")
                self.msg_entry.delete(0, tk.END)
            except:
                messagebox.showerror("Hata", "Mesaj gönderilemedi.")

    def append_log(self, text, tag=None):
        """GUI'ye yazı ekler"""
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, text + "\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')


if __name__ == "__main__":
    ChatClientGUI()