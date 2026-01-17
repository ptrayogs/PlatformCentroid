import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Konfigurasi Halaman
st.set_page_config(page_title="Admin - GeoAI SLS Generator", layout="wide")

st.title("🛠️ Admin Dashboard: SLS Center Generator")
st.markdown("""
Aplikasi ini akan menghitung titik tengah SLS berdasarkan **konsentrasi titik bangunan** (Mean Center). 
Jika dalam satu SLS tidak terdapat titik bangunan, maka titik akan diletakkan pada *Representative Point*.
""")

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
                # Load Data
                gdf_sls = gpd.read_file(sls_file, engine='pyogrio')
                gdf_bldg = gpd.read_file(bldg_file, engine='pyogrio')

                # Memastikan CRS menggunakan WGS84 (EPSG:4326)
                if gdf_sls.crs != "EPSG:4326":
                    gdf_sls = gdf_sls.to_crs(epsg=4326)
                if gdf_bldg.crs != "EPSG:4326":
                    gdf_bldg = gdf_bldg.to_crs(epsg=4326)

                # 2. Spatial Join
                # idsls bangunan -> 'idsls_left', idsls poligon -> 'idsls_right'
                joined = gpd.sjoin(gdf_bldg, gdf_sls, predicate='within')

                if joined.empty:
                    st.error("Tidak ada titik bangunan yang ditemukan di dalam poligon SLS.")
                else:
                    # 3. Hitung Mean Center
                    joined['x_coord'] = joined.geometry.x
                    joined['y_coord'] = joined.geometry.y

                    # Deteksi kolom ID pasca join
                    group_col = 'idsls_right' if 'idsls_right' in joined.columns else 'idsls'
                    
                    mean_centers = joined.groupby(group_col).agg({'x_coord': 'mean', 'y_coord': 'mean'}).reset_index()
                    mean_centers = mean_centers.rename(columns={group_col: 'idsls'})
                    
                    # Membuat geometry point dari hasil rata-rata
                    mean_centers['geometry_center'] = mean_centers.apply(lambda row: Point(row['x_coord'], row['y_coord']), axis=1)

                    # 4. Gabungkan kembali ke data SLS Master
                    final_gdf = gdf_sls.merge(mean_centers[['idsls', 'geometry_center']], on='idsls', how='left')

                    # Fallback Mechanism
                    # Kita buat GeoSeries secara eksplisit agar bisa mengambil .y dan .x
                    rep_points = final_gdf.geometry.representative_point()
                    final_points = final_gdf['geometry_center'].fillna(rep_points)
                    
                    # Mengubah hasil fillna menjadi GeoSeries agar atribut .x dan .y tersedia
                    final_points_gs = gpd.GeoSeries(final_points)

                    # 5. Ekstrak Latitude dan Longitude
                    final_gdf['latitude'] = final_points_gs.y
                    final_gdf['longitude'] = final_points_gs.x

                    # 6. Export Data
                    output_cols = ['nmkec', 'nmdesa', 'nmsls', 'idsls', 'latitude', 'longitude']
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