import streamlit as st
import sqlite3
import pandas as pd
import time
import plotly.express as px

# Sayfa Ayarları (Geniş Ekran)
st.set_page_config(
    page_title="🏭 IoT Fabrika Kontrol Paneli",
    page_icon="📊",
    layout="wide"
)

# Başlık
st.title("🏭 Endüstriyel IoT & Kestirimci Bakım Paneli")
st.markdown("---")

# Veritabanı Dosyası
DB_FILE = "bakim_loglari.db"

def load_data():
    """Veritabanından son 100 kaydı çeker"""
    try:
        conn = sqlite3.connect(DB_FILE)
        # En son veriler en üstte olsun diye DESC sıralıyoruz
        df = pd.read_sql("SELECT * FROM sensor_log ORDER BY id DESC LIMIT 100", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Veritabanı okunamadı: {e}")
        return pd.DataFrame()

# --- VERİYİ HAZIRLA ---
df = load_data()

if not df.empty:
    # 'raw_data' sütunu "L,300,310,1500,40,10" gibi string geliyor.
    # Bunu parçalayıp sayısal sütunlara çevirmeliyiz.
    try:
        # Virgül ile ayırıp yeni sütunlar yap
        split_data = df['raw_data'].str.split(',', expand=True)
        
        # Sütun isimlerini ata (Client kodundaki sıraya göre)
        split_data.columns = ['Machine_Type', 'Air_Temp', 'Process_Temp', 'Speed', 'Torque', 'Tool_Wear']
        
        # Sayısal değerlere çevir
        split_data['Air_Temp'] = pd.to_numeric(split_data['Air_Temp'])
        split_data['Process_Temp'] = pd.to_numeric(split_data['Process_Temp'])
        split_data['Speed'] = pd.to_numeric(split_data['Speed'])
        split_data['Torque'] = pd.to_numeric(split_data['Torque'])
        split_data['Tool_Wear'] = pd.to_numeric(split_data['Tool_Wear'])
        
        # Ana tabloyla birleştir
        df = pd.concat([df, split_data], axis=1)
        
    except Exception as e:
        st.warning("Veri formatı ayrıştırılırken hata oluştu. Henüz yeterli veri olmayabilir.")

    # --- KPI KARTLARI (ÜST BİLGİ) ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_logs = len(df)
    critical_errors = len(df[df['tahmin'] != 'No Failure'])
    last_machine = df.iloc[0]['gonderen'] if not df.empty else "-"
    last_status = df.iloc[0]['tahmin'] if not df.empty else "-"

    col1.metric("📊 Toplam Veri Kaydı", total_logs)
    col2.metric("🚨 Tespit Edilen Riskler", critical_errors, delta_color="inverse")
    col3.metric("👤 Son Aktif Makine", last_machine)
    
    # Duruma göre renkli gösterim
    if last_status == "No Failure":
        col4.metric("✅ Son Durum", "NORMAL", delta_color="normal")
    else:
        col4.metric("⚠️ Son Durum", last_status, delta_color="inverse")

    st.markdown("---")

    # --- GRAFİKLER BÖLÜMÜ ---
    st.subheader("📈 Canlı Sensör Trendleri")
    
    # Grafik Alanı (2 Sütun)
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        st.info("🔥 Sıcaklık Analizi")
        # Plotly ile interaktif grafik
        fig_temp = px.line(df, x=df.index, y=['Air_Temp', 'Process_Temp'], 
                           title='Hava ve İşlem Sıcaklığı', markers=True)
        st.plotly_chart(fig_temp, use_container_width=True)

    with g_col2:
        st.info("⚙️ Tork ve Hız Analizi")
        # İki eksenli grafik yerine alt alta iki çizgi
        fig_mech = px.line(df, x=df.index, y=['Torque', 'Speed'], 
                           title='Tork ve Dönüş Hızı', markers=True)
        st.plotly_chart(fig_mech, use_container_width=True)

    # --- DETAYLI TABLO ---
    st.subheader("📋 Son Kayıtlar ve Yapay Zeka Tahminleri")
    
    # Tabloyu güzelleştir (Sadece önemli sütunları göster)
    display_df = df[['tarih', 'gonderen', 'tahmin', 'guven_orani', 'Torque', 'Tool_Wear', 'Speed']]
    
    # Riskli olanları kırmızı boyamak için fonksiyon
    def highlight_risk(val):
        color = 'red' if val != 'No Failure' else 'green'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        display_df.style.applymap(highlight_risk, subset=['tahmin']),
        use_container_width=True
    )

else:
    st.warning("⚠️ Henüz veri bulunamadı. Lütfen 'Client' üzerinden simülasyonu başlatın.")

# --- OTOMATİK YENİLEME (REAL-TIME) ---
# Sayfanın her 2 saniyede bir yenilenmesini sağlar
time.sleep(2)
st.rerun()