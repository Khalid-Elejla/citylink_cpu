import streamlit as st
from control_center.map import map_page
from control_center.alerts import alerts_page
from control_center.dashboard import dashboard_page
from apps.parking.parking import parking_page
from tools.search import search_page
from tools.history import history_page
from streamlit_extras.app_logo import add_logo

# Set up the Streamlit page
st.set_page_config(
    page_title="City Link",
    page_icon="logo.png",
    layout="wide",
)


# Display the floating logo
# st.markdown('<img src="logo.png" class="floating-logo">', unsafe_allow_html=True)

# st.markdown("""
#         <style>
#                .css-18e3th9 {
#                     padding-top: 0rem;
#                     padding-bottom: 10rem;
#                     padding-left: 5rem;
#                     padding-right: 5rem;
#                 }
#                .css-1d391kg {
#                     padding-top: 3.5rem;
#                     padding-right: 1rem;
#                     padding-bottom: 3.5rem;
#                     padding-left: 1rem;
#                 }
#         </style>
#         """, unsafe_allow_html=True)

import streamlit as st



st.markdown("""
    <style>
    /* Reduce padding and margin for the sidebar header */
    div[data-testid="stSidebarHeader"] {
        padding: 10px; /* Adjust as needed */
        margin: 0;     /* Adjust as needed */
    }

    /* Reduce padding around the logo image */
    div[data-testid="stSidebarHeader"] img[data-testid="stLogo"] {
        width: 100px;  /* Adjust width as needed */
        height: auto;  /* Maintain aspect ratio */
        margin: 0;     /* Adjust margin if needed */
    }

    /* Reduce padding around the sidebar collapse button */
    div[data-testid="stSidebarCollapseButton"] {
        padding: 2px;  /* Adjust as needed */
        margin: 0;     /* Adjust as needed */
    }

    /* Adjust button padding */
    div[data-testid="stSidebarCollapseButton"] button {
        padding: 2px;  /* Adjust as needed */
    }
        
    /* Adjust button padding */
    div[data-testid="stAppViewBlockContainer"]
    {
        padding-top: 30px; /* Adjust as needed */
        margin: 0;     /* Adjust as needed */
    }
            
  
    </style>
    
    """, unsafe_allow_html=True)


# # Inject the custom CSS to control the logo size
# st.markdown("""
#     <style>
#     img[alt="Logo"] {
#         width: 90px;  /* Adjust size as needed */
#         height: 80px;  /* Maintain aspect ratio */
#         padding-bottom: 10px;

#     }
#     </style>
#     """, unsafe_allow_html=True)

# Display the logo using st.logo or st.image
st.logo("logo.png")

# st.logo(
#     "cropped-logo-10-300x131.png",
#     link="https://streamlit.io/gallery",
#     icon_image="logom.jpeg",
# )


st.markdown("""
    <style>
    div[data-testid="stSidebarCollapseButton"] {
        padding: 2px;  /* Adjust this value as needed */
    }
    </style>
    """, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

map = st.Page(map_page, title="Map", icon=":material/map:", default=True)
alerts = st.Page(alerts_page, title="Alerts", icon=":material/notification_important:")#,default=True)
dashboard = st.Page(dashboard_page, title="Dashboard", icon=":material/dashboard:")

parking = st.Page(parking_page, title="Parking", icon=":material/local_taxi:")

search = st.Page(search_page, title="Search", icon=":material/search:")
history = st.Page(history_page, title="History", icon=":material/history:")

# Define your pages
def navigate_to_page(page_name):
    st.session_state.page = page_name
    st.switch_page(page_name)

if "page" not in st.session_state:
    st.session_state.page = "map"
if st.session_state.page == "alerts":
    navigate_to_page(alerts)



if st.session_state.logged_in:

    pg = st.navigation(
        {
            "Account": [logout_page],
            "Control Center": [map, alerts, dashboard],
            "apps": [parking],
            "Tools": [search, history],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()

#########################################
# import streamlit as st
# from control_center.map import map_page
# from control_center.alerts import alerts_page
# from control_center.dashboard import dashboard_page
# from apps.parking import parking_page
# from tools.search import search_page
# from tools.history import history_page



# # Set up the Streamlit page
# st.set_page_config(
#     page_title="City Link",
#     page_icon=":world_globe:",
#     layout="wide",
# )

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# def login():
#     if st.button("Log in"):
#         st.session_state.logged_in = True
#         st.rerun()

# def logout():
#     if st.button("Log out"):
#         st.session_state.logged_in = False
#         st.rerun()


# login_page = st.Page(login, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# map = st.Page(map_page, title="Map", icon=":material/map:", default=True)
# alerts = st.Page(alerts_page, title="Alerts", icon=":material/notification_important:")#,default=True)
# dashboard = st.Page(dashboard_page, title="Dashboard", icon=":material/dashboard:")

# parking = st.Page(parking_page, title="Parking", icon=":material/local_taxi:")

# search = st.Page(search_page, title="Search", icon=":material/search:")
# history = st.Page(history_page, title="History", icon=":material/history:")

# ###################################################################################
# # if "current_page" not in st.session_state:
# #     st.session_state.current_page = "Dashboard"  # Set your default page here

# pages = {
#     "Login": login,
#     "Logout": logout,
#     "Map": map_page,
#     "Alerts": alerts_page,
#     "Dashboard": dashboard_page,
#     "Parking": parking_page,
#     "Search": search_page,
#     "History": history_page,
# }


# if "page_name" not in st.session_state:
#     st.session_state.page_name = "Dashboard"  # Set default page

# if st.session_state.page_name == "Alerts":
#     print("AAAAAAAAAAAAAAAAAAAAAAAAAA")
#     st.switch_page(alerts)
#     st.session_state.page_name == ""
#     # pg.run()

# # # Navigation logic
# # if st.session_state.logged_in:
# #     if st.session_state.current_page in pages:
# #         pages[st.session_state.current_page]()
# #     else:
# #         st.error("Page not found.")
# ###################################################################################
# if st.session_state.logged_in:
#     pg = st.navigation(
#         {
#             "Account": [logout_page],
#             "Control Center": [map, alerts, dashboard],
#             "apps": [parking],
#             "Tools": [search, history],
#         }
#     )
# else:
#     pg = st.navigation([login_page])

# pg.run()