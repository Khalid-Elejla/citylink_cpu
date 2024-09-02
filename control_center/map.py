import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium, folium_static
from folium import PolyLine
from utils.route_utils import construct_osrm_url, get_trip_data
import os
from datetime import datetime, time
from matplotlib import pyplot as plt

def calculate_Emergency_kpis(df):
    # Strip trailing '*' from column names
    df.columns = df.columns.str.rstrip('*')

    # Check if required columns exist
    required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' is missing from the DataFrame")

    today = datetime.today().date()

    # Function to parse time whether it includes seconds or not
    def parse_time(t):
        try:
            return pd.to_datetime(t, format='%H:%M:%S').time()
        except ValueError:
            try:
                return pd.to_datetime(t, format='%H:%M').time()
            except ValueError:
                raise ValueError(f"Time format for '{t}' is incorrect")

    # Ensure 'Open Time' and 'Closure Time' are in time format
    df['Open Time'] = df['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
    df['Closure Time'] = df['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

    # Combine with today's date to create datetime objects
    df['Open Time'] = df['Open Time'].apply(lambda x: datetime.combine(today, x))
    df['Closure Time'] = df['Closure Time'].apply(lambda x: datetime.combine(today, x))

    # Calculate the mean emergency closure time
    # emergency_closure_time = (df['Closure Time'] - df['Open Time']).mean()
    emergency_closure_time = (df['Closure Time'] - df['Open Time']).mean()
    emergency_closure_time = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

    # Calculate Closure Percentage
    closure_percentage = (df['Status'] == 'Closed').mean() * 100

    # Calculate Satisfaction Rate
    satisfaction_rate = df['Satisfaction'].str.lower().apply(lambda x: x == 'sattisfied').mean() * 100

    # Calculate Emergency Numbers as the number of unique incidents based on Latitude and Longitude
    df['Location'] = df[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
    emergency_numbers = df['Location'].nunique()

    # Placeholder for Expected Emergency Alarm
    expected_emergency_alarm = "To be calculated based on relationships"

    # Return a dictionary with all the calculated KPIs
    return {
        "Closure Percentage": closure_percentage,
        "Emergency Closure Time": emergency_closure_time,
        "Satisfaction Rate": satisfaction_rate,
        "Emergency Numbers": emergency_numbers,
        "Expected Emergency Alarm": expected_emergency_alarm
    }

def calculate_workforce_kpis(df):
    # Strip trailing '*' from column names
    df.columns = df.columns.str.rstrip('*')

    # Check if required columns exist
    required_columns = ['Open-Time', 'Closure Time', 'Status', 'Evaluation', 'Complain today']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' is missing from the DataFrame")

    today = datetime.today().date()

    # Function to parse time whether it includes seconds or not
    def parse_time(t):
        try:
            return pd.to_datetime(t, format='%H:%M:%S').time()
        except ValueError:
            try:
                return pd.to_datetime(t, format='%H:%M').time()
            except ValueError:
                raise ValueError(f"Time format for '{t}' is incorrect")

    # Ensure 'Open-Time' and 'Closure Time' are in time format
    df['Open-Time'] = df['Open-Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
    df['Closure Time'] = df['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

    # Combine with today's date to create datetime objects
    df['Open-Time'] = df['Open-Time'].apply(lambda x: datetime.combine(today, x))
    df['Closure Time'] = df['Closure Time'].apply(lambda x: datetime.combine(today, x))

    # Calculate the average working hours
    working_hours = (df['Closure Time'] - df['Open-Time']).mean()
    working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

    # Calculate Operation Percentage (Active/Total)
    total_operations = len(df)
    active_operations = (df['Status'] == 'Active').sum()
    operation_percentage = (active_operations / total_operations) * 100

    # Calculate Evaluation Rate
    total_evaluations = df['Evaluation'].sum()
    total_responses = len(df)
    evaluation_rate = total_evaluations / total_responses if total_responses > 0 else 0

    # Calculate Complain Numbers
    complain_numbers = df['Complain today'].sum()

    # Placeholder for Expected Complaints Alarm
    expected_complains_alarm = "To be calculated based on relationships"



    # Generate Pie Chart for Operations
    status_counts = df['Operation'].value_counts()  # Group by status and count
    fig, ax = plt.subplots(figsize=(4, 4))

    # Set figure and axes backgrounds to transparent
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')

    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90,textprops={'color': 'white'})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Operations Status Distribution')

    # # Display the pie chart in Streamlit
    # st.pyplot(fig)

    # Return a dictionary with all the calculated KPIs
    return {
        "Operation Percentage": operation_percentage,
        "Working Hours": working_hours_str,
        "Evaluation Rate": evaluation_rate,
        "Complain Numbers": complain_numbers,
        "Expected Complains Alarm": expected_complains_alarm,
        "fig": fig,
    }





# Load data from Excel, including multiple sheets
def load_data(data_url):
    return pd.read_excel(data_url, sheet_name=None)  # Load all sheets into a dict

# Cache the creation of the map with all markers
@st.cache_data(show_spinner=False)
def create_map(df, coordinates):
    m = folium.Map(
        tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
        attr='OpenStreetMap HOT'
    )
    m.fit_bounds(coordinates)

    asterisk_columns = [col for col in df.columns if col.endswith('*')]
    tooltip_col = asterisk_columns[0] if asterisk_columns else None
    asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

    for idx, row in df.iterrows():
        popup_content = "".join(
            f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
        )
        
        if 'Status*' in row:
            icon_color = 'blue' if row['Status*'] == 'Closed' else 'red'    
        else:
            icon_color = 'blue'

        marker_id = f"marker_{idx}"
        marker = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"""
                <div>
                    <b>{row[tooltip_col]}</b><br>
                    {popup_content}
                    <br><br>
                    <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
                </div>
            """,
            tooltip=row[tooltip_col] if tooltip_col else '',
            icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
        )
        marker.add_to(m)

    return m

def map_page():
    # List files in the data folder
    data_folder = 'data'
    files = [f for f in os.listdir(data_folder) if f.endswith('.xlsx') and not f.startswith('~$')]
    file_options = [os.path.splitext(f)[0] for f in files]  # Remove file extension

    # Initialize session state if not already
    if 'dynamic_mode' not in st.session_state:
        st.session_state['dynamic_mode'] = False
    if 'route_coords' not in st.session_state:
        st.session_state['route_coords'] = []

    # Columns layout
    col1, col2, col3, col4, col5, col6 = st.columns([3, 7, 6,4, 1, 1], gap="small", vertical_alignment="bottom")

    with col1:
        st.write('Select System')

    with col2:
        selected_file = st.selectbox('Select System', file_options, label_visibility="collapsed")

    # Check if a file has been selected
    if selected_file:
        data_url = os.path.join(data_folder, f"{selected_file}.xlsx")
        sheets_dict = load_data(data_url)
        sheet_names = list(sheets_dict.keys())

        with col3:
            selected_sheet = st.selectbox('Select Sheet', sheet_names)

        df = sheets_dict[selected_sheet]
        coordinates = df[['Latitude', 'Longitude']].values.tolist()

        # Extract the file name without extension for the header
        file_name = selected_file.capitalize()

        with col5:
            if st.button('🗺️'):
                if len(coordinates) >= 2:
                    # Check if number of waypoints exceeds OSRM limit
                    if len(coordinates) > 100:
                        st.session_state['warning_message'] = "The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations."
                    else:
                        osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
                        trip_data = get_trip_data(osrm_url)

                        route_coords = trip_data['trips'][0]['geometry']['coordinates']
                        route_coords = [(lat, lon) for lon, lat in route_coords]

                        st.session_state['route_coords'] = route_coords
                        st.session_state['warning_message'] = None  # Clear warning message

        with col6:
            if st.button("🖱️"):
                st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']

        # Create the map with markers
        m = create_map(df, coordinates)

        # Add route to the map if it exists
        if st.session_state['route_coords']:
            PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

        # Conditionally render the map based on mode
        if st.session_state['dynamic_mode']:
            st_data = st_folium(m, height=500, width=1040)
        else:
            st_data = folium_static(m, height=500, width=1040)

        # Handle marker clicks in dynamic mode
        if st.session_state['dynamic_mode'] and st_data.get("last_object_clicked_popup") is not None:
            st.session_state['selected_marker'] = st_data["last_object_clicked_popup"]

        # Display data table with collapsible view
        with st.expander(f'{file_name} - {selected_sheet} Table', expanded=True):
            st.dataframe(df, width=950, height=300)

        # Display warning message in the sidebar if it exists
        if 'warning_message' in st.session_state and st.session_state['warning_message']:
            st.sidebar.warning(st.session_state['warning_message'])

        if selected_sheet == "Emergency" :
                # Call the KPI calculation function
                kpis = calculate_Emergency_kpis(df)

                # Display the KPIs
                st.write("## Key Performance Indicators (KPIs)")
                col11, col12, col13, col14, col15 = st.columns([1,2,1,1,1])
                col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
                col12.metric("Emergency Closure Time", f"{kpis['Emergency Closure Time']}")
                col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
                col14.metric("Emergency Numbers", kpis['Emergency Numbers'])
                col15.write(f"Expected Emergency Alarm: {kpis['Expected Emergency Alarm']}")

        elif selected_sheet == "Workforce" :
            # Call the KPI calculation function
            kpis = calculate_workforce_kpis(df)

            # Display the KPIs in Streamlit
            st.write("## Key Performance Indicators (KPIs)")
            col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
            col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
            col12.metric("Working Hours", kpis['Working Hours'])
            col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
            col14.metric("Complain Numbers", kpis['Complain Numbers'])
            col15.write(f"Expected Complains Alarm: {kpis['Expected Complains Alarm']}")


            col21, col22, col23 = st.columns([1,2,1])
            # # Display the pie chart in Streamlit
            with col22:
                st.pyplot(kpis['fig'])


# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import st_folium, folium_static
# from folium import PolyLine
# from utils.route_utils import construct_osrm_url, get_trip_data
# import os

# # Load data from Excel, including multiple sheets
# def load_data(data_url):
#     return pd.read_excel(data_url, sheet_name=None)  # Load all sheets into a dict

# # Cache the creation of the map with all markers
# @st.cache_data(show_spinner=False)
# def create_map(df, coordinates):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )
#     m.fit_bounds(coordinates)

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     print(f"asterisk_columns: {asterisk_columns}")
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None
#     print(f"tooltip_col: {tooltip_col}")
#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
        
#         if 'Status*' in row:
#             icon_color = 'blue' if row['Status*'] == 'Closed' else 'red'    
#         else:
#             icon_color = 'blue'
#         # icon_color = 'blue' if 'Status*' in row and row['Status*'] == 'Closed' else 'red'

#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)

#     return m

# def map_page():
    
#     # List files in the data folder
#     data_folder = 'data'
#     files = [f for f in os.listdir(data_folder) if f.endswith('.xlsx') and not f.startswith('~$')]
#     file_options = [os.path.splitext(f)[0] for f in files]  # Remove file extension

#     # Initialize session state if not already
#     if 'dynamic_mode' not in st.session_state:
#         st.session_state['dynamic_mode'] = False
#     if 'route_coords' not in st.session_state:
#         st.session_state['route_coords'] = []

#     # Columns layout
#     col1, col2, col3, col4, col5 = st.columns([3, 5, 10, 1, 1], gap="small", vertical_alignment="bottom")

#     with col1:
#         st.write('Select System')

#     with col2:
#         selected_file = st.selectbox('Select System', file_options, label_visibility="collapsed")

#     # Check if a file has been selected
#     if selected_file:
#         data_url = os.path.join(data_folder, f"{selected_file}.xlsx")
#         sheets_dict = load_data(data_url)
#         sheet_names = list(sheets_dict.keys())

#         with col3:
#             selected_sheet = st.selectbox('Select Sheet', sheet_names)

#         df = sheets_dict[selected_sheet]
#         coordinates = df[['Latitude', 'Longitude']].values.tolist()

#         # Extract the file name without extension for the header
#         file_name = selected_file.capitalize()

#         with col4:
#             if st.button('🗺️'):
#                 if len(coordinates) >= 2:
#                     osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
#                     trip_data = get_trip_data(osrm_url)

#                     route_coords = trip_data['trips'][0]['geometry']['coordinates']
#                     route_coords = [(lat, lon) for lon, lat in route_coords]

#                     st.session_state['route_coords'] = route_coords

#         with col5:
#             if st.button("🖱️"):
#                 st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']

#         # Create the map with markers
#         m = create_map(df, coordinates)

#         # Add route to the map if it exists
#         if st.session_state['route_coords']:
#             PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

#         # Conditionally render the map based on mode
#         if st.session_state['dynamic_mode']:
#             st_data = st_folium(m, height=500, width=1020)
#         else:
#             st_data = folium_static(m, height=500, width=1020)

#         # Handle marker clicks in dynamic mode
#         if st.session_state['dynamic_mode'] and st_data.get("last_object_clicked_popup") is not None:
#             st.session_state['selected_marker'] = st_data["last_object_clicked_popup"]

#         # Display data table with collapsible view
#         with st.expander(f'{file_name} - {selected_sheet} Table', expanded=True):
#             st.dataframe(df, width=950, height=300)



####################################################################################
# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import st_folium, folium_static
# from folium import PolyLine
# from utils.route_utils import construct_osrm_url, get_trip_data
# import os

# # Load data from CSV
# def load_data(data_url):
#     # return pd.read_csv(data_url)
#     return pd.read_excel(data_url)

# # Cache the creation of the map with all markers
# @st.cache_data(show_spinner=False)
# def create_map(df, coordinates):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )
#     m.fit_bounds(coordinates)

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None
#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
        
#     if 'Status*' in row:
#         icon_color = 'blue' if row['Status*'] == 'Closed' else 'red'
#     else:
#         icon_color = 'blue'

#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)

#     return m

# def map_page():
    
#     # List files in the data folder
#     data_folder = 'data'
#     # files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

#     files = [f for f in os.listdir(data_folder) if f.endswith('.xlsx')]
#     file_options = [os.path.splitext(f)[0] for f in files]  # Remove file extension

#     # Initialize session state if not already
#     if 'dynamic_mode' not in st.session_state:
#         st.session_state['dynamic_mode'] = False
#     if 'route_coords' not in st.session_state:
#         st.session_state['route_coords'] = []

#     # Columns layout
#     col1, col2, col3, col4, col5 = st.columns([3, 5,10, 1, 1], gap="small", vertical_alignment="bottom")

#     with col1:
#         st.write('Select System')

#     with col2:
#         selected_file = st.selectbox('Select System', file_options,label_visibility="collapsed")

#     # Check if a file has been selected
#     if selected_file:
#         # data_url = os.path.join(data_folder, f"{selected_file}.csv")  # Add .csv extension
#         data_url = os.path.join(data_folder, f"{selected_file}.xlsx")  # Add .csv extension
#         df = load_data(data_url)
#         coordinates = df[['Latitude', 'Longitude']].values.tolist()

#         # Extract the file name without extension for the header
#         file_name = selected_file.capitalize()

#         with col4:
#             # Handle route calculation
#             if st.button('🗺️'):
#                 if len(coordinates) >= 2:
#                     osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
#                     trip_data = get_trip_data(osrm_url)

#                     route_coords = trip_data['trips'][0]['geometry']['coordinates']
#                     route_coords = [(lat, lon) for lon, lat in route_coords]

#                     st.session_state['route_coords'] = route_coords

#         with col5:
#             if st.button("🖱️"):
#                 st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']

#         # Create the map with markers
#         m = create_map(df, coordinates)

#         # Add route to the map if it exists
#         if st.session_state['route_coords']:
#             PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

#         # Conditionally render the map based on mode
#         if st.session_state['dynamic_mode']:
#             st_data = st_folium(m, height=500, width=1020)
#         else:
#             st_data = folium_static(m, height=500, width=1020)

#         # Handle marker clicks in dynamic mode
#         if st.session_state['dynamic_mode'] and st_data.get("last_object_clicked_popup") is not None:
#             st.session_state['selected_marker'] = st_data["last_object_clicked_popup"]

#         # Display data table with collapsible view
#         with st.expander(f'{file_name} Table', expanded=True):
#             st.dataframe(df, width=950, height=300)
#######################################################################################

# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import st_folium, folium_static
# from folium import PolyLine
# from utils.route_utils import construct_osrm_url, get_trip_data
# import os

# # Load data from CSV
# def load_data(data_url):
#     return pd.read_csv(data_url)

# # Cache the creation of the map with all markers
# @st.cache_data(show_spinner=False)
# def create_map(df, coordinates):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )

#     m.fit_bounds(coordinates)

#     # Identify columns with '*' and the tooltip column
#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None
#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     for idx, row in df.iterrows():
#         # Create popup content dynamically based on columns with '*'
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
        
#         icon_color = 'blue' if row['Status*'] == 'Closed' else 'red'

#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)

#     return m

# def map_page():
#     # List files in the data folder
#     data_folder = 'data'
#     files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
#     file_options = [os.path.splitext(f)[0] for f in files]  # Remove file extension

#     # add buttons to control map
#     col1, col2, col3, col4, col5 = st.columns([1, 3,5, 2,2], gap="small", vertical_alignment="bottom")  # Adjust column widths as needed
#     with col1:
#         st.write('Select System')
#     with col2:
#         selected_file = st.selectbox('', file_options)

#     with col4:
#         # Handle route calculation
#         if st.button('🗺️'):
#             if len(coordinates) >= 2:
#                 osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
#                 trip_data = get_trip_data(osrm_url)

#                 route_coords = trip_data['trips'][0]['geometry']['coordinates']
#                 route_coords = [(lat, lon) for lon, lat in route_coords]

#                 st.session_state['route_coords'] = route_coords
#     with col5:
#         if st.button("🖱️"):
#             st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']

#     if selected_file:
#         data_url = os.path.join(data_folder, f"{selected_file}.csv")  # Add .csv extension
#         df = load_data(data_url)
#         coordinates = df[['Latitude', 'Longitude']].values.tolist()

#         # Extract the file name without extension for the header
#         file_name = selected_file.capitalize()

#         # Toggle between static and dynamic modes
#         if 'dynamic_mode' not in st.session_state:
#             st.session_state['dynamic_mode'] = False

#         # if st.button('Toggle Dynamic Mode'):
#         #     st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']

#         # Create the map with markers
#         m = create_map(df, coordinates)

#         # Handle route calculation
#         # if st.button('Calculate Best Route'):
#         #     if len(coordinates) >= 2:
#         #         osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
#         #         trip_data = get_trip_data(osrm_url)

#         #         route_coords = trip_data['trips'][0]['geometry']['coordinates']
#         #         route_coords = [(lat, lon) for lon, lat in route_coords]

#         #         st.session_state['route_coords'] = route_coords

#         # Check if a route exists and add it to the map
#         if 'route_coords' in st.session_state:
#             PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

#         # Conditionally render the map based on mode
#         if st.session_state['dynamic_mode']:
#             st_data = st_folium(m, height=500, width=1020)
#         else:
#             st_data = folium_static(m, height=500, width=1020)

#         # Handle marker clicks in dynamic mode
#         if st.session_state['dynamic_mode'] and st_data.get("last_object_clicked_popup") is not None:
#             st.session_state['selected_marker'] = st_data["last_object_clicked_popup"]

#         # Display data table with collapsible view
#         with st.expander(f'{file_name} Table', expanded=True):
#             st.dataframe(df, width=950, height=300)
