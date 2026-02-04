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
    
iamhere = 0
iamhere_return = 0
findmeabike = False
findmeadock = False

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
        input_street_return = st.text_input("Calle", "")
        input_city_return = st.text_input("Ciudad", "CDMX") # No me convence dejar este
        input_country_return = st.text_input("País", "México") # No me convence dejar este
        findmeadock = st.button("¡Encuentrame un anclaje!", type="primary")
        
        if findmeadock:
            if input_street_return != "":
                iamhere_return = geocode(input_street_return + " " + input_city_return + " " + input_country_return)
                if iamhere_return == "":
                    st.subheader(":red[Dirección no valida]")
            else:
                st.subheader(":red[Dirección no valida]")

if bike_method == "Devolver" and findmeadock == False:
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
    

if bike_method == "Rentar" and findmeabike == False:
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

if findmeabike:
    if input_street != "":
        if iamhere != "":
            chosen_station = get_bike_availability(iamhere, df)  # Get bike availability (id, lat, lon)
            center = iamhere  # Center the map on user's location
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')  # Create a detailed map
            for _, row in df.iterrows():
                marker_color = get_marker_color(row['num_bikes_available'])  # Determine marker color based on bikes available
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                       f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                       , max_width=300)
                ).add_to(m1)
            folium.Marker(
                location=iamhere,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup="Rent your bike here.",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere)  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(label=":green[Travel Time (min)]", value=duration)  # Display travel time

if findmeadock:
    if input_street_return != "":
        if iamhere_return != "":
            chosen_station = get_dock_availability(iamhere_return, df)  # Get dock availability (id, lat, lon)
            center = iamhere_return  # Center the map on user's location
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')  # Create a detailed map
            for _, row in df.iterrows():
                marker_color = get_marker_color(row['num_bikes_available'])  # Determine marker color based on bikes available
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                       f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                       , max_width=300)
                ).add_to(m1)
            folium.Marker(
                location=iamhere_return,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup="Return your bike here.",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere_return)  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(label=":green[Travel Time (min)]", value=duration)  # Display travel time