import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Konfigurasi Halaman
st.set_page_config(page_title="Admin - GeoAI SLS Generator", layout="wide")

st.title("🛠️ Admin Dashboard: SLS Center Generator")
st.markdown("""
Aplikasi ini akan menghitung titik tengah SLS berdasarkan **konsentrasi titik bangunan** (Mean Center). 
Jika dalam satu SLS tidak terdapat titik bangunan, maka titik akan diletakkan pada *Representative Point* (titik di dalam poligon).
""")

---

# 1. Upload Section
col1, col2 = st.columns(2)
with col1:
    sls_file = st.file_uploader("Upload Peta SLS (GeoJSON)", type=['geojson'])
with col2:
    bldg_file = st.file_uploader("Upload Titik Bangunan (GeoJSON)", type=['geojson'])

if sls_file and bldg_file:
    if st.button("🚀 Jalankan Proses Generate"):
        try:
            with st.spinner("Sedang memproses data spasial..."):
                # Load Data menggunakan pyogrio agar lebih cepat
                gdf_sls = gpd.read_file(sls_file, engine='pyogrio')
                gdf_bldg = gpd.read_file(bldg_file, engine='pyogrio')

                # Memastikan CRS menggunakan WGS84 (EPSG:4326) agar hasil Lat/Long benar
                if gdf_sls.crs != "EPSG:4326":
                    gdf_sls = gdf_sls.to_crs(epsg=4326)
                if gdf_bldg.crs != "EPSG:4326":
                    gdf_bldg = gdf_bldg.to_crs(epsg=4326)

                # 2. Spatial Join
                # Menggabungkan titik bangunan ke dalam poligon SLS
                # idsls dari bldg menjadi 'idsls_left', idsls dari sls menjadi 'idsls_right'
                joined = gpd.sjoin(gdf_bldg, gdf_sls, predicate='within')

                if joined.empty:
                    st.error("Tidak ada titik bangunan yang ditemukan di dalam poligon SLS. Pastikan kedua file berada di wilayah yang sama.")
                else:
                    # 3. Hitung Mean Center
                    # Rumus Mean Center:
                    # \bar{X} = \frac{\sum x_i}{n}, \bar{Y} = \frac{\sum y_i}{n}
                    joined['x'] = joined.geometry.x
                    joined['y'] = joined.geometry.y

                    # Kita gunakan 'idsls_right' karena ini adalah ID asli dari poligon SLS
                    group_col = 'idsls_right' if 'idsls_right' in joined.columns else 'idsls'
                    
                    mean_centers = joined.groupby(group_col).agg({'x': 'mean', 'y': 'mean'}).reset_index()
                    mean_centers = mean_centers.rename(columns={group_col: 'idsls'})
                    
                    # Membuat geometry point dari hasil rata-rata
                    mean_centers['geometry_center'] = mean_centers.apply(lambda row: Point(row['x'], row['y']), axis=1)

                    # 4. Gabungkan kembali ke data SLS Master
                    final_gdf = gdf_sls.merge(mean_centers[['idsls', 'geometry_center']], on='idsls', how='left')

                    # Fallback Mechanism: Jika SLS kosong bangunan, gunakan representative_point
                    # representative_point dijamin selalu berada di dalam poligon
                    final_gdf['final_geometry'] = final_gdf['geometry_center'].fillna(final_gdf.geometry.representative_point())

                    # Ekstrak Latitude dan Longitude
                    final_gdf['latitude'] = final_gdf['final_geometry'].y
                    final_gdf['longitude'] = final_gdf['final_geometry'].x

                    # 5. Export Data
                    # Memilih kolom yang dibutuhkan untuk Viewer
                    output_cols = ['nmkec', 'nmdesa', 'nmsls', 'idsls', 'latitude', 'longitude']
                    
                    # Memastikan semua kolom target tersedia di data original
                    available_cols = [c for c in output_cols if c in final_gdf.columns]
                    export_df = pd.DataFrame(final_gdf[available_cols])

                    st.success(f"✅ Berhasil memproses {len(export_df)} SLS!")
                    st.dataframe(export_df.head(10))

                    # Download Button
                    csv = export_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download master_sls.csv",
                        data=csv,
                        file_name="master_sls.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")

else:
    st.info("Silakan upload kedua file GeoJSON untuk memulai.")