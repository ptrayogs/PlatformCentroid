import streamlit as st
import pandas as pd

st.set_page_config(page_title="Centroid SLS", layout="centered")

# Styling agar tampilan optimal di smartphone
st.markdown("""
    <style>
    .stSelectbox { margin-bottom: 20px; }
    .stCode { background-color: #f0f2f6; border-radius: 8px; }
    /* Memperbesar teks dropdown untuk layar sentuh */
    .stSelectbox div[data-baseweb="select"] {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 Centroid Tagging SLS")
st.write("Temukan Centroid SLS di Kabupaten Pesawaran")

@st.cache_data
def load_data():
    try:
        # Membaca data master
        df = pd.read_csv("master_sls.csv")
        
        # MEMASTIKAN KODE 3 DIGIT (PENTING)
        # zfill(3) akan mengubah '10' menjadi '010'
        df['kdkec_str'] = df['kdkec'].astype(str).str.zfill(3)
        df['kddesa_str'] = df['kddesa'].astype(str).str.zfill(3)
        
        # Membuat kolom label gabungan [kode] Nama
        df['label_kec'] = "[" + df['kdkec_str'] + "] " + df['nmkec']
        df['label_desa'] = "[" + df['kddesa_str'] + "] " + df['nmdesa']
        
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return None

df = load_data()

if df is not None:
    # 1. Filter Kecamatan
    list_kec = sorted(df['label_kec'].unique().tolist())
    selected_kec_label = st.selectbox("1. Pilih Kecamatan", ["-- Pilih --"] + list_kec)
    
    if selected_kec_label != "-- Pilih --":
        # Filter data berdasarkan kecamatan yang dipilih
        filtered_kec = df[df['label_kec'] == selected_kec_label]
        
        # 2. Filter Desa
        list_desa = sorted(filtered_kec['label_desa'].unique().tolist())
        selected_desa_label = st.selectbox("2. Pilih Desa", ["-- Pilih --"] + list_desa)
        
        if selected_desa_label != "-- Pilih --":
            # Tampilkan Hasil SLS berdasarkan desa yang dipilih
            results = filtered_kec[filtered_kec['label_desa'] == selected_desa_label]
            
            st.divider()
            st.subheader(f"Daftar SLS ({len(results)})")

            for _, row in results.iterrows():
                # Menampilkan Nama SLS sebagai judul kartu
                with st.expander(f"🏠 {row['nmsls']}"):
                    
                    # 1. Menampilkan IDSLS
                    st.write(f"**IDSLS :** `{row['idsls']}`")
                    
                    # 2. Menampilkan Titik Tengah Koordinat
                    coords = f"{row['latitude']},{row['longitude']}"
                    st.write("**Titik Tengah Koordinat :**")
                    # Menggunakan st.code agar user di HP tinggal tap untuk copy
                    st.code(coords, language=None)
                    
                    # 3. Link ke Google Maps
                    maps_link = f"https://www.google.com/maps?q={coords}"
                    st.link_button("🗺️ Buka di Google Maps", maps_link)
else:
    st.warning("⚠️ File 'master_sls.csv' belum tersedia. Pastikan Admin sudah menjalankan proses generate.")