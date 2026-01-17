import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

st.set_page_config(page_title="Admin - SLS Generator", layout="wide")

st.title("🛠️ Admin Dashboard: SLS Center Generator")
st.write("Upload data GeoJSON untuk menghasilkan file Master CSV.")

col1, col2 = st.columns(2)
with col1:
    sls_file = st.file_uploader("Batas SLS (GeoJSON)", type=['geojson'])
with col2:
    bldg_file = st.file_uploader("Titik Bangunan (GeoJSON)", type=['geojson'])

if sls_file and bldg_file:
    if st.button("Generate Master Data"):
        with st.spinner("Menghitung Mean Center Spasial..."):
            # Load & Align CRS
            gdf_sls = gpd.read_file(sls_file)
            gdf_bldg = gpd.read_file(bldg_file)
            if gdf_sls.crs != gdf_bldg.crs:
                gdf_bldg = gdf_bldg.to_crs(gdf_sls.crs)

            # Spatial Join
            joined = gpd.sjoin(gdf_bldg, gdf_sls, predicate='within')

            # Hitung Mean Center (Rata-rata Koordinat)
            joined['x'] = joined.geometry.x
            joined['y'] = joined.geometry.y
            mean_centers = joined.groupby('index_right').agg({'x': 'mean', 'y': 'mean'}).reset_index()
            
            # Buat geometry point hasil rata-rata
            mean_centers['geometry_center'] = mean_centers.apply(lambda row: Point(row['x'], row['y']), axis=1)
            
            # Gabung kembali ke SLS untuk mapping atribut & fallback
            final_gdf = gdf_sls.copy()
            final_gdf = final_gdf.merge(mean_centers[['index_right', 'geometry_center']], 
                                        left_index=True, right_on='index_right', how='left')

            # Fallback: Jika SLS kosong bangunan, gunakan representative_point (pasti di dalam poligon)
            final_gdf['final_geometry'] = final_gdf['geometry_center'].fillna(final_gdf.geometry.representative_point())
            
            # Ekstrak Lat/Long untuk CSV (EPSG:4326)
            final_gdf = final_gdf.to_crs(epsg=4326)
            final_gdf['latitude'] = final_gdf['final_geometry'].y
            final_gdf['longitude'] = final_gdf['final_geometry'].x

            # Pilih kolom yang dibutuhkan saja (sesuaikan nama kolom di GeoJSON kamu)
            # Contoh: nm_kec, nm_desa, nm_sls
            export_df = pd.DataFrame(final_gdf[['nm_kec', 'nm_desa', 'nm_sls', 'latitude', 'longitude']])
            
            st.success("Berhasil di-generate!")
            st.dataframe(export_df.head())

            # Download CSV
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download master_sls.csv", data=csv, file_name="master_sls.csv", mime="text/csv")
