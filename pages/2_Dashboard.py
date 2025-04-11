import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title='Dashb Mortalidad', layout='wide', page_icon=":dart:")
st.title("DASHBOARD DE MORTALIDAD POR CÁNCER DE MAMA EN COLOMBIA")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    data = pd.read_excel("data.xlsx")
    poblacion = pd.read_excel("data_40M.xlsx")
    muertes_mensuales = pd.read_excel("dep_anio_mes.xlsx")
    return data, poblacion, muertes_mensuales

# Cargar los datos
datos, data_40M, dep_anio_mes = cargar_datos()

# Sidebar: filtros
departamentos = ["Todos"] + sorted(dep_anio_mes['NOMBRE_DPT'].unique())
años = sorted(dep_anio_mes['ANIO_DEF'].unique())
años_opciones = ["Todos"] + años
anio_sel = st.selectbox("Selecciona un año", años_opciones, index=0)
depto_sel = st.selectbox("Selecciona el departamento", departamentos, index=0)

# KPIs
total_muertes = datos.shape[0]

filtro_data = datos.copy()
if depto_sel != "Todos":
    filtro_data = filtro_data[filtro_data['Nombre_Departamento'] == depto_sel]
if anio_sel != "Todos":
    filtro_data = filtro_data[filtro_data['año_def'] == anio_sel]
total_filtrado = filtro_data.shape[0]

# Mostrar KPIs a la izquierda
with st.container():
    st.subheader("Indicadores Clave")
    st.metric("🔢 Total de muertes registradas", f"{total_muertes:,}")
    st.metric("🔍 Registros filtrados", f"{total_filtrado:,}")

# Filtrar según selección
filtro_muertes = dep_anio_mes.copy()
if depto_sel != "Todos":
    filtro_muertes = filtro_muertes[filtro_muertes['NOMBRE_DPT'] == depto_sel]
if anio_sel != "Todos":
    filtro_muertes = filtro_muertes[filtro_muertes['ANIO_DEF'] == anio_sel]

# Agrupar por MES_DEF y sumar muertes
muertes_mensuales = filtro_muertes.groupby('MES_DEF')['NUM_MUERTES'].sum().reindex([
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
], fill_value=0)

# Población para cálculo de tasas
filtro_poblacion = data_40M.copy()
if depto_sel != "Todos":
    filtro_poblacion = filtro_poblacion[filtro_poblacion['NOMBRE_DPT'] == depto_sel]
if anio_sel != "Todos":
    filtro_poblacion = filtro_poblacion[filtro_poblacion['ANIO'] == anio_sel]

# Calcular tasa de mortalidad mensual
if not filtro_poblacion.empty:
    if anio_sel == "Todos":
        total_mujeres = filtro_poblacion['TOTAL_MUJERES'].median()
    else:
        total_mujeres = filtro_poblacion['TOTAL_MUJERES'].sum()
    tasas = muertes_mensuales / total_mujeres * 100000
else:
    tasas = muertes_mensuales * 0

total_tasa = tasas.sum()

# Gráfico de cascada (Waterfall) - tonos rosados
fig1 = go.Figure(go.Waterfall(
    name="Tasa mensual",
    orientation="v",
    measure=["relative"] * len(tasas) + ["total"],
    x=list(tasas.index) + ['Total'],
    y=list(tasas.values) + [total_tasa],
    text=[f"{v:.2f}" for v in tasas.values] + [f"{total_tasa:.2f}"],
    decreasing={"marker": {"color": "#D46A92"}},  # rosa oscuro
    increasing={"marker": {"color": "#F58FB0"}},  # rosa medio
    totals={"marker": {"color": "#E75480"}}       # rosa fuerte
))
titulo = f"Tasa de Mortalidad Mensual"
if depto_sel != "Todos":
    titulo += f" en {depto_sel}"
if anio_sel != "Todos":
    titulo += f" ({anio_sel})"
else:
    titulo += " (Todos los años)"

fig1.update_layout(
    title=titulo,
    yaxis_title="Tasa por 100,000 mujeres",
    xaxis_title="Mes",
    showlegend=False,
    height=450
)
st.plotly_chart(fig1)

# Gráfico de barras por municipio - tonos rosados
filtro_data = datos.copy()
if depto_sel != "Todos":
    filtro_data = filtro_data[filtro_data['Nombre_Departamento'] == depto_sel]
if anio_sel != "Todos":
    filtro_data = filtro_data[filtro_data['año_def'] == anio_sel]

muertes_municipios = filtro_data.groupby('Nombre_Municipio').size().reset_index(name='Cantidad')
titulo_municipio = f"Muertes por Municipio"
if depto_sel != "Todos":
    titulo_municipio += f" en {depto_sel}"
if anio_sel != "Todos":
    titulo_municipio += f" ({anio_sel})"
else:
    titulo_municipio += " (Todos los años)"

fig2 = px.bar(muertes_municipios.sort_values(by='Cantidad', ascending=False),
              x='Nombre_Municipio', y='Cantidad',
              title=titulo_municipio,
              labels={'Cantidad': 'Número de Muertes'},
              height=450,
              color_discrete_sequence=["#F58FB0"]  # rosa medio
              )
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2)

# Gráfico de barras por grupo de edad - tonos rosados
grupos = filtro_data.groupby('grupo_edad').size().reset_index(name='Cantidad')
fig3 = px.bar(grupos.sort_values(by='Cantidad', ascending=False),
              x='grupo_edad', y='Cantidad',
              title=f"Distribución por Grupo de Edad",
              labels={'Cantidad': 'Número de Muertes'},
              height=450,
              color_discrete_sequence=["#D46A92"]  # rosa oscuro
              )
st.plotly_chart(fig3)

# Pie chart por estado civil - tonos rosados personalizados
estado = filtro_data.groupby('estado_civil').size().reset_index(name='Cantidad')
color_palette = ["#ffb6c1", "#ff69b4", "#db7093", "#c71585", 
                 "#ff1493", "#e60073", "#cc0033", "#b20000"]

fig4 = px.pie(estado, names='estado_civil', values='Cantidad',
              title=f"Estado Civil de Fallecidas",
              height=450,
              color_discrete_sequence=color_palette
              )
st.plotly_chart(fig4)

