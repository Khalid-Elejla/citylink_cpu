import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium import PolyLine
from utils.route_utils import construct_osrm_url, get_trip_data
from control_center.alerts import alerts_page


def map_page():
    # # Get query parameters
    # query_params = st.query_params
    # st.write(f"query param: {query_params}")
    
    # # Check if a specific marker was clicked
    # if 'marker_id' in query_params:
    #     selected_marker_id = query_params['marker_id']  # Get the marker_id from query parameters
    #     st.session_state.selected_marker = selected_marker_id
    #     st.write(f"Selected Marker ID: {selected_marker_id}")
    # else:
    #     st.write("No marker selected.")


    
    # Load the data from CSV
    # data_url = 'data/street_lights.csv'
    # df = pd.read_csv(data_url)

    data_url = 'data/complains.csv'
    df = pd.read_csv(data_url)
    # print(len(df))


    # Initialize the map centered on Riyadh
    m = folium.Map(
        location=[24.7136, 46.6753],  # Center the map on Riyadh
        zoom_start=15,
        tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
        attr='OpenStreetMap HOT'
    )

    # Extract coordinates for routing
    coordinates = df[['Latitude', 'Longitude']].values.tolist()

    m.fit_bounds(coordinates)
    # Add markers with custom icons and JavaScript for handling clicks
    for idx, row in df.iterrows():
        # icon_color = 'green' if f"marker_{idx}" == st.session_state.get('selected_marker') else ('blue' if row['Status'] == 'Working' else 'red')
        icon_color = 'green' if f"marker_{idx}" == st.session_state.get('selected_marker') else ('blue' if row['Status'] == 'Closed' else 'red')

        # marker_id = f"marker_{idx}"
        # marker = folium.Marker(
        #     location=[row['Latitude'], row['Longitude']],
        #     popup=f"""
        #         <div>
        #             <b>{row['Location_Name']}</b><br>
        #             Status: {row['Status']}<br>
        #             Last Inspection: {row['Last_Inspection_Date']}
        #             <br><br>
                    
        #             <a href="?marker_id={marker_id}" style="text-decoration:none;">
        #             <button>Select Marker</button>
        #             </a>
        #         </div>
        #     """,
        #     tooltip=row['Location_Name'],
        #     icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
        # )

        marker_id = f"marker_{idx}"
        marker = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"""
                <div>
                    <b>{row['Type']}</b><br>
                    Status: {row['Status']}<br>
                    Satisfaction: {row['Satisfaction']}
                    <br><br>
                    
                    <a href="?marker_id={marker_id}" style="text-decoration:none;">
                    <button>Select Marker</button>
                    </a>
                </div>
            """,
            tooltip=row['Location_Name'],
            icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
        )
        marker.add_to(m)

    # Button to trigger route calculation
    if st.button('Calculate Best Route'):
        if len(coordinates) >= 2:
            osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
            trip_data = get_trip_data(osrm_url)

            # Extract the route geometry and plot it on the map
            route_coords = trip_data['trips'][0]['geometry']['coordinates']
            # The OSRM response returns coordinates as [lon, lat], so we need to reverse them to [lat, lon]
            route_coords = [(lat, lon) for lon, lat in route_coords]

            # Store the route coordinates in the session state
            st.session_state['route_coords'] = route_coords

    # Check if route_coords is in the session state and render the route if present
    if 'route_coords' in st.session_state:
        PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

    # Render the Folium map in Streamlit
    map_data = st_folium(m, height=500, width=700)
    st.write(map_data)
    
    # Check if a marker was clicked
    if map_data.get("last_object_clicked_popup") is not None:
        print(map_data["last_object_clicked_popup"])
        # st.session_state.page = "alerts"
        # st.rerun()