from helper_functions import *
import pandas as pd 
import streamlit as st

# Se cargan los urls
station_url = "https://gbfs.mex.lyftbikes.com/gbfs/en/station_status.json"
latlon_url = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json"

# Se guardan los datos para la visualización

df_station = query_station_status(station_url)
df_latlon = get_station_latlon(latlon_url)
df = join_latlon(df_station, df_latlon)

st.title("CDMX Bike Share Station Status") #Provicional
st.markdown("This dashboard tracks bike availability at each bike share station in CDMX") # Provicional
# st.dataframe(df) # visualiza el dataframe en la app
col1, col2,col3 = st.columns(3)

with col1:
    st.metric(label = "Bicicletas disponibles", value = sum(df["num_bikes_available"]))
with col2:
    st.metric(label = "Estaciones con bicicletas disponibles", value = len(df[df["num_bikes_available"]>0]))
with col3:
    st.metric(label = "Número de anclajes vacios", value = len(df[df["num_docks_available"]>0]))

with st.sidebar:
    st.selectbox(
        "¿Buscas rentar o devolverbicicleta?", 
        ("Rentar", "Devolver")
    )