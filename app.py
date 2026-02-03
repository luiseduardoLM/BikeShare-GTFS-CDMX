from helper_functions import *
import pandas as pd 
import streamlit as st
import folium
from streamlit_folium import folium_static

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
    bike_method = st.selectbox(
        "¿Buscas rentar o devolverbicicleta?", 
        ("Rentar", "Devolver")
    )
    if bike_method == "Rentar":
        st.header("¿Donde te localizas?")
        input_street = st.text_input("Calle", "")
        input_city = st.text_input("Ciudad", "CDMX") # No me convence dejar este
        input_country = st.text_input("País", "México") # No me convence dejar este
        drive = st.checkbox("Estoy ahí") # True or False
        findmeabike = st.button("¡Encuentrame una bici!", type="primary")
        
        if findmeabike:
            if input_street != "":
                iamhere = geocode(input_street + " " + input_city + " " + input_country)
                if iamhere == "":
                    st.subheader(":red[Dirección no valida]")
            else:
                st.subheader(":red[Dirección no valida]")
    elif bike_method == "Devolver":
        st.header("¿Donde te localizas?")
        input_street = st.text_input("Calle", "")
        input_city = st.text_input("Ciudad", "CDMX") # No me convence dejar este
        input_country = st.text_input("País", "México") # No me convence dejar este
        findmeadock = st.button("¡Encuentrame un anclaje!", type="primary")
        
        if findmeadock:
            if input_street != "":
                iamhere_return = geocode(input_street + " " + input_city + " " + input_country)
                if iamhere_return == "":
                    st.subheader(":red[Dirección no valida]")
            else:
                st.subheader(":red[Dirección no valida]")

# Mapa
# Creamos el mapa centrado en el angel de la independencia
center = [19.427, -99.16771] #

m = folium.Map(location=center, zoom_start=13, tiles="cartodbpositron")

for _, row in df.iterrows():
    marker_color = get_marker_color(row["num_bikes_available"])
    folium.CircleMarker(
        location = [row["lat"], row["lon"]],
        radius = 2,
        color = marker_color,
        fill=True,
        fill_color=marker_color,
        fill_opacity=0.7,
        popup=folium.Popup(f"Station ID: {row["station_id"]}<br>"
                           f"Total Bikes Available: {row["num_bikes_available"]}<br>",
                           max_width = 300)
        ).add_to(m)
    
# Despliega el mapa
folium_static(m)