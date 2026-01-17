import streamlit as st
import pandas as pd

st.set_page_config(page_title="Centroid SLS", layout="centered")

# Styling agar tombol dan teks lebih besar di layar HP
st.markdown("""
    <style>
    .stSelectbox { margin-bottom: 20px; }
    .stCode { background-color: #f0f2f6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 Centroid Tagging SLS")
st.write("Temukan Centroid SLS di Kabupaten Pesawaran")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("master_sls.csv")
        # Membuat kolom label gabungan [kode] Nama
        # Pastikan kolom kdkec dan kddesa ada di master_sls.csv
        df['label_kec'] = "[" + df['kdkec'].astype(str) + "] " + df['nmkec']
        df['label_desa'] = "[" + df['kddesa'].astype(str) + "] " + df['nmdesa']
        return df
    except Exception as e:
        return None

df = load_data()

if df is not None:
    # Filter Kecamatan menggunakan label baru
    list_kec = sorted(df['label_kec'].unique().tolist())
    selected_kec_label = st.selectbox("1. Pilih Kecamatan", ["-- Pilih --"] + list_kec)
    
    if selected_kec_label != "-- Pilih --":
        # Filter data berdasarkan label kecamatan yang dipilih
        filtered_kec = df[df['label_kec'] == selected_kec_label]
        
        # Filter Desa menggunakan label baru
        list_desa = sorted(filtered_kec['label_desa'].unique().tolist())
        selected_desa_label = st.selectbox("2. Pilih Desa", ["-- Pilih --"] + list_desa)
        
        if selected_desa_label != "-- Pilih --":
            # Tampilkan Hasil SLS berdasarkan filter label desa
            results = filtered_kec[filtered_kec['label_desa'] == selected_desa_label]
            
            st.divider()
            st.subheader(f"Daftar SLS ({len(results)})")

            for _, row in results.iterrows():
                # Menampilkan Nama SLS di expander
                with st.expander(f"🏠 {row['nmsls']}"):
                    coords = f"{row['latitude']},{row['longitude']}"
                    
                    st.write("Klik koordinat di bawah untuk copy:")
                    st.code(coords, language=None)
                    
                    # Tombol buka peta
                    maps_link = f"https://www.google.com/maps?q={coords}"
                    st.link_button("🗺️ Lihat di Google Maps", maps_link)
else:
    st.warning("⚠️ File 'master_sls.csv' tidak ditemukan atau format kolom tidak sesuai (kdkec/kddesa tidak ada).")