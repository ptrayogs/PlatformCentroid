import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

st.set_page_config(page_title="Admin - GeoAI SLS", layout="wide")

st.title("🛠️ Admin Dashboard: SLS Center Generator")
st.write("Gunakan menu ini untuk memproses data spasial mentah menjadi master data.")

col1, col2 = st.columns(2)
with col1:
    sls_file = st.file_uploader("Upload Peta SLS (GeoJSON)", type=['geojson'])
with col2:
    bldg_file = st.file_uploader("Upload Titik Bangunan (GeoJSON)", type=['geojson'])

if sls_file and bldg_file:
    if st.button("🚀 Jalankan Proses Generate"):
        with st.spinner("Sedang menghitung titik tengah berbasis kepadatan bangunan..."):
            # 1. Load Data (Menggunakan pyogrio agar cepat)
            gdf_sls = gpd.read_file(sls_file, engine='pyogrio')
            gdf_bldg = gpd.read_file(bldg_file, engine='pyogrio')
            
            # Pastikan CRS ke WGS84 (Lat/Long)
            gdf_sls = gdf_sls.to_crs(epsg=4326)
            gdf_bldg = gdf_bldg.to_crs(epsg=4326)

            # 2. Spatial Join (Menentukan titik bangunan ada di SLS mana)
            # Kita gunakan spatial join 'within' agar akurat secara geografis
            joined = gpd.sjoin(gdf_bldg, gdf_sls, predicate='within')

            # 3. Hitung Mean Center per SLS
            # Mengambil rata-rata koordinat x dan y dari semua bangunan di dalam 1 SLS
            joined['x'] = joined.geometry.x
            joined['y'] = joined.geometry.y
            
            mean_centers = joined.groupby('idsls').agg({'x': 'mean', 'y': 'mean'}).reset_index()
            mean_centers['geometry_center'] = mean_centers.apply(lambda row: Point(row['x'], row['y']), axis=1)
            
            # 4. Gabungkan ke data SLS original (untuk fallback SLS kosong)
            final_gdf = gdf_sls.merge(mean_centers[['idsls', 'geometry_center']], on='idsls', how='left')

            # Fallback: Jika tidak ada bangunan, gunakan titik representatif (di dalam poligon)
            final_gdf['final_geometry'] = final_gdf['geometry_center'].fillna(final_gdf.geometry.representative_point())
            
            # 5. Siapkan Data untuk CSV
            final_gdf['latitude'] = final_gdf['final_geometry'].y
            final_gdf['longitude'] = final_gdf['final_geometry'].x
            
            # Pilih kolom sesuai data kamu
            export_df = pd.DataFrame(final_gdf[['nmkec', 'nmdesa', 'nmsls', 'idsls', 'latitude', 'longitude']])
            
            st.success("✅ Selesai! Titik tengah berhasil dihitung.")
            st.dataframe(export_df.head())

            # Tombol Download untuk Admin
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download master_sls.csv",
                data=csv,
                file_name="master_sls.csv",
                mime="text/csv"
            )