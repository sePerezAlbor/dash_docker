import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

st.set_page_config(page_title='Mapa de Mortalidad', layout='wide', page_icon = "images\colombia.png" )

@st.cache_data
def cargar_datos():
    url_muertes = 'muertes_completo.xlsx'      
    url_poblacion = 'data_40M.xlsx'
    url_geo = 'colombia_departamentos.geojson'

    muertes = pd.read_excel(url_muertes)
    poblacion = pd.read_excel(url_poblacion)
    geo = gpd.read_file(url_geo)

    return muertes, poblacion, geo

muertes_completo, data_40M, colombia_geo = cargar_datos()

st.title('MAPA DE MORTALIDAD POR CÁNCER DE MAMA EN COLOMBIA')

# Sidebar
st.sidebar.header('Filtros')

# Años disponibles
anios_disponibles = sorted([int(a) for a in muertes_completo['ANIO_DEF'].unique()])
año_min = min(anios_disponibles)
año_max = max(anios_disponibles)

año_inicio, año_fin = st.sidebar.select_slider(
    'RANGO DE AÑOS',
    options=anios_disponibles,
    value=(año_min, año_max)
)

k = st.sidebar.selectbox('Valor de k', [100, 1000, 10000, 100000, 1000000])

# Filtrado
muertes_filtrado = muertes_completo[
    (muertes_completo['ANIO_DEF'] >= año_inicio) & (muertes_completo['ANIO_DEF'] <= año_fin)
]
pob_filtrada = data_40M[
    (data_40M['ANIO'] >= año_inicio) & (data_40M['ANIO'] <= año_fin)
]

# Cálculo de tasa de mortalidad
muertes_agg = muertes_filtrado.groupby('NOMBRE_DPT')['TOTAL_MUERTES'].sum().reset_index()
if año_inicio == año_fin:
    pob_agg = pob_filtrada.groupby('NOMBRE_DPT')['TOTAL_MUJERES'].sum().reset_index()
else:
    pob_agg = pob_filtrada.groupby('NOMBRE_DPT')['TOTAL_MUJERES'].median().reset_index()

tasa = pd.merge(muertes_agg, pob_agg, on='NOMBRE_DPT')
tasa['Tasa_Mortalidad'] = (tasa['TOTAL_MUERTES'] / tasa['TOTAL_MUJERES']) * k

# Métricas
mayor = tasa.loc[tasa['Tasa_Mortalidad'].idxmax()]
menor = tasa.loc[tasa['Tasa_Mortalidad'].idxmin()]
promedio = tasa['Tasa_Mortalidad'].mean()

# Sidebar visual
with st.sidebar:
    st.subheader('MAYOR TASA DE MORTALIDAD')
    st.image('images/up-arrow.png', width=30)
    st.markdown(f"**{mayor['NOMBRE_DPT']}**: {mayor['Tasa_Mortalidad']:.2f}")

    st.subheader('TASA DE MORTALIDAD PROMEDIO')
    st.image('images/arrow.png', width=30)
    st.markdown(f"**{promedio:.2f}**")

    st.subheader('MENOR TASA DE MORTALIDAD')
    st.image('images/down-arrow.png', width=30)
    st.markdown(f"**{menor['NOMBRE_DPT']}**: {menor['Tasa_Mortalidad']:.2f}")

# Unir con geodatos
colombia_geo = colombia_geo.rename(columns={'NOMBRE_DPT': 'NOMBRE_DPT'})
tasa_mapa = colombia_geo.merge(tasa, on='NOMBRE_DPT', how='left')



fig = px.choropleth_mapbox(
    tasa_mapa,
    geojson=tasa_mapa.geometry,
    locations=tasa_mapa.index,
    color='Tasa_Mortalidad',
    hover_name='NOMBRE_DPT',
    color_continuous_scale='Plotly3',  
    range_color=(0, tasa['Tasa_Mortalidad'].max()),
    mapbox_style='open-street-map',  # Otros: 'open-street-map', 'satellite-streets', etc.
    zoom=4.5,
    center={"lat": 4.5709, "lon": -74.2973},
    opacity=0.7,
    height=850
)



fig.update_layout(margin={'r':0, 't':0, 'l':0, 'b':0})

st.plotly_chart(fig, use_container_width=True)

