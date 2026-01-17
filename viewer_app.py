import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cek Titik SLS", layout="centered")

# CSS untuk membuat tampilan lebih ramah Mobile
st.markdown("""
    <style>
    .stSelectbox { margin-bottom: -10px; }
    .css-1r6slb0 { padding: 10px; border-radius: 10px; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 Geotagging SLS")

@st.cache_data
def get_data():
    try:
        return pd.read_csv("master_sls.csv")
    except:
        return None

df = get_data()

if df is not None:
    # Filter Berjenjang
    kec = st.selectbox("Pilih Kecamatan", ["-- Pilih --"] + sorted(df['nm_kec'].unique().tolist()))
    
    if kec != "-- Pilih --":
        desa_list = sorted(df[df['nm_kec'] == kec]['nm_desa'].unique().tolist())
        desa = st.selectbox("Pilih Desa", ["-- Pilih --"] + desa_list)
        
        if desa != "-- Pilih --":
            filtered = df[(df['nm_kec'] == kec) & (df['nm_desa'] == desa)]
            st.write(f"Menampilkan **{len(filtered)}** SLS")
            
            for _, row in filtered.iterrows():
                with st.expander(f"🏠 {row['nm_sls']}"):
                    coords = f"{row['latitude']},{row['longitude']}"
                    
                    st.write("Salin Koordinat:")
                    st.code(coords, language=None)
                    
                    maps_link = f"https://www.google.com/maps?q={coords}"
                    st.link_button("Buka di Google Maps", maps_link)
else:
    st.error("File master_sls.csv belum tersedia. Silakan hubungi Admin.")
