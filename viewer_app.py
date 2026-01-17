import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pencarian Titik SLS", layout="centered")

# Styling agar tombol dan teks lebih besar di layar HP
st.markdown("""
    <style>
    .stSelectbox { margin-bottom: 20px; }
    .stCode { background-color: #f0f2f6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 Geotagging SLS")
st.write("Cari SLS dan salin koordinatnya untuk aplikasi lain.")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("master_sls.csv")
    except:
        return None

df = load_data()

if df is not None:
    # Filter Kecamatan
    list_kec = sorted(df['nmkec'].unique().tolist())
    selected_kec = st.selectbox("1. Pilih Kecamatan", ["-- Pilih --"] + list_kec)
    
    if selected_kec != "-- Pilih --":
        # Filter Desa
        list_desa = sorted(df[df['nmkec'] == selected_kec]['nmdesa'].unique().tolist())
        selected_desa = st.selectbox("2. Pilih Desa", ["-- Pilih --"] + list_desa)
        
        if selected_desa != "-- Pilih --":
            # Tampilkan Hasil SLS
            results = df[(df['nmkec'] == selected_kec) & (df['nmdesa'] == selected_desa)]
            st.divider()
            st.subheader(f"Daftar SLS ({len(results)})")

            for _, row in results.iterrows():
                with st.expander(f"🏠 {row['nmsls']}"):
                    coords = f"{row['latitude']},{row['longitude']}"
                    
                    st.write("Klik koordinat di bawah untuk copy:")
                    # st.code akan membuat box yang kalau di-tap di HP biasanya langsung select all
                    st.code(coords, language=None)
                    
                    # Tombol buka peta
                    maps_link = f"https://www.google.com/maps?q={coords}"
                    st.link_button("🗺️ Lihat di Google Maps", maps_link)
else:
    st.warning("⚠️ File 'master_sls.csv' tidak ditemukan. Admin perlu meng-upload data terlebih dahulu.")