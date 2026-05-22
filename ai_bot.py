import socket
import ssl
import time
import os
import sqlite3
import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import google.generativeai as genai

# --- AYARLAR ---
HOST = '127.0.0.1'
PORT = 12345
BOT_NICKNAME = "🤖 AI_Maintenance_Bot"
CSV_FILE = "predictive_maintenance.csv"
DB_FILE = "bakim_loglari.db"

# --- API CONNECTION & MODEL SELECTION ---
# Set the GEMINI_API_KEY environment variable before running.
# Example (Linux/macOS): export GEMINI_API_KEY="your_api_key_here"
# Example (Windows):     set GEMINI_API_KEY=your_api_key_here
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

model_gemini = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # SENİN HESABINDAKİ MODELLER (Önem sırasına göre)
    candidate_models = [
        "gemini-2.5-flash",       # İlk Tercih: En yeni ve hızlı
        "gemini-2.0-flash",       # Alternatif: Çok kararlı
        "gemini-flash-latest",    # Genel takma ad
        "gemini-2.0-flash-lite",  # Hafif sürüm
        "gemini-2.5-pro"          # En güçlüsü (Yavaş olabilir)
    ]
    
    print("\n🔄 Gemini Modeli Bağlanıyor...")
    for model_name in candidate_models:
        try:
            print(f"   ⏳ Deneniyor: {model_name}...", end=" ")
            test_model = genai.GenerativeModel(model_name)
            
            # Gerçek bir bağlantı testi yapalım
            response = test_model.generate_content("test")
            
            if response:
                model_gemini = test_model
                print(f"✅ BAŞARILI!")
                print(f"🎯 Aktif Model: {model_name}")
                break
        except Exception as e:
            print(f"❌ (Hata: {e})")
            continue

    if not model_gemini:
        print("\n⚠️ KRİTİK HATA: Hiçbir model çalışmadı. API Key'ini kontrol et.")
else:
    print("⚠️ UYARI: GEMINI_API_KEY bulunamadı! Sohbet özelliği devre dışı.")

# --- VERİTABANI ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarih TEXT,
                    gonderen TEXT,
                    tahmin TEXT,
                    guven_orani REAL,
                    raw_data TEXT
                )''')
    conn.commit()
    conn.close()

def log_to_db(sender, prediction, confidence, raw_data):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO sensor_log (tarih, gonderen, tahmin, guven_orani, raw_data) VALUES (?, ?, ?, ?, ?)",
                  (tarih, sender, prediction, confidence, raw_data))
        conn.commit()
        conn.close()
        print(f"💾 DB Kayıt: {prediction}")
    except Exception as e:
        print(f"DB Hatası: {e}")

# --- AKSİYON (MAIL SİMÜLASYONU) ---
def trigger_action(sender, failure_type):
    alert_msg = f"""
    🛑 ACİL DURUM RAPORU 🛑
    -------------------------
    Zaman: {datetime.datetime.now()}
    Makine: {sender}
    Tespit Edilen Arıza: {failure_type}
    
    Aksiyon: Bakım ekibine e-posta gönderildi.
    Sistem durumu: KRİTİK.
    """
    try:
        with open("ACIL_DURUM_RAPORU.txt", "a", encoding="utf-8") as f:
            f.write(alert_msg + "\n\n")
        print(f"⚡ AKSİYON ALINDI: {failure_type} raporlandı.")
    except: pass

# --- AI MODELİ (Random Forest) ---
class MaintenanceBrain:
    def __init__(self, csv_path):
        self.model = None
        self.le_type = LabelEncoder()
        self.csv_path = csv_path
        self.train_model()

    def train_model(self):
        print("\n⚙️  YAPAY ZEKA EĞİTİLİYOR (Random Forest)...")
        try:
            if not os.path.exists(self.csv_path):
                print("❌ HATA: CSV dosyası yok! Bot başlatılamadı.")
                return
            df = pd.read_csv(self.csv_path)
            df = df.drop(['UDI', 'Product ID', 'Target'], axis=1)
            df['Type'] = self.le_type.fit_transform(df['Type'])
            X = df.drop('Failure Type', axis=1)
            y = df['Failure Type']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            acc = accuracy_score(y_test, self.model.predict(X_test))
            print(f"✅ Model Hazır! Başarı Oranı: %{acc*100:.2f}")
        except Exception as e:
            print(f"❌ Eğitim Hatası: {e}")

    def predict_failure(self, data_str):
        if not self.model: return "Model Yüklü Değil", 0
        try:
            parts = data_str.split(',')
            input_data = pd.DataFrame({
                'Type': [parts[0]],
                'Air temperature [K]': [float(parts[1])],
                'Process temperature [K]': [float(parts[2])],
                'Rotational speed [rpm]': [float(parts[3])],
                'Torque [Nm]': [float(parts[4])],
                'Tool wear [min]': [float(parts[5])]
            })
            try: input_data['Type'] = self.le_type.transform(input_data['Type'])
            except: input_data['Type'] = 0 
            prediction = self.model.predict(input_data)[0]
            proba = np.max(self.model.predict_proba(input_data)) * 100
            return prediction, proba
        except Exception as e:
            return f"Hata: {e}", 0

# --- ANA DÖNGÜ ---
def start_bot():
    init_db()
    brain = MaintenanceBrain(CSV_FILE)

    client = None
    while client is None:
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client = context.wrap_socket(raw_socket, server_hostname=HOST)
            client.connect((HOST, PORT))
        except:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((HOST, PORT))
            except:
                time.sleep(2)

    try:
        msg = client.recv(1024).decode('utf-8')
        if 'NICK' in msg:
            client.send(BOT_NICKNAME.encode('utf-8'))
    except: pass

    print(f"🟢 {BOT_NICKNAME} Sunucuya Bağlandı ve Hazır!")

    while True:
        try:
            message = client.recv(4096).decode('utf-8', errors='ignore')
            if not message: break
            
            if message.startswith(BOT_NICKNAME): continue 

            # --- 1. SOHBET (Gemini) ---
            if "TELEMETRY|" not in message and ("@ai" in message.lower() or "@bot" in message.lower()):
                print(f"💬 Soru Geldi: {message}")
                
                if ":" in message:
                    content = message.split(":", 1)[1]
                else:
                    content = message
                
                clean_content = content.lower().replace("@ai", "").replace("@bot", "").strip()
                
                if clean_content and model_gemini:
                    try:
                        # Cevabı üret
                        ans = model_gemini.generate_content(clean_content).text.strip()
                        response = f"{BOT_NICKNAME}: {ans}"
                        client.send(response.encode('utf-8'))
                    except Exception as e:
                        print(f"API Hatası: {e}")
                        client.send(f"{BOT_NICKNAME}: Şu an bağlantıda sorun var.".encode('utf-8'))
                elif not model_gemini:
                    client.send(f"{BOT_NICKNAME}: Yapay zeka modülü aktif değil.".encode('utf-8'))

            # --- 2. SENSÖR VERİSİ ---
            elif "TELEMETRY|" in message:
                try:
                    sender = message.split(":")[0]
                    content = message.split("TELEMETRY|")[1].strip()
                    print(f"📥 Veri Analizi: {content}")
                    
                    result, confidence = brain.predict_failure(content)
                    log_to_db(sender, result, confidence, content)

                    if result != "No Failure":
                        trigger_action(sender, result)
                        report_msg = f"REPORT|🚨 RİSK TESPİTİ!\nMakine: {sender}\nArıza: {result.upper()}\nGüven: %{confidence:.1f}\nDurum: KRİTİK"
                    else:
                        report_msg = f"REPORT|✅ Analiz Normal\nMakine: {sender}\nDurum: Stabil\nGüven: %{confidence:.1f}"
                    
                    client.send(report_msg.encode('utf-8'))

                except Exception as e:
                    print(f"Telemetry Hatası: {e}")

        except Exception as e:
            print(f"Bağlantı Koptu: {e}")
            break

if __name__ == "__main__":
    start_bot()