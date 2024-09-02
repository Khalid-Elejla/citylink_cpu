import streamlit as st
import tempfile
import json
from .detect_parking import run_parking_detection

DEMO_VIDEO = 'new.mp4'
PARKING_SPOTS_FILE = 'apps/parking/parking_spots.json'

def load_parking_spots(video_filename):
    with open(PARKING_SPOTS_FILE, 'r') as file:
        data = json.load(file)
    return [list(map(tuple, spots)) for spots in data.get(video_filename, [])]

def parking_page():
    use_webcam = st.sidebar.button('Use Webcam')
    video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])

    model_path = "apps/parking/models/vehicle_detector.pt"
    parking_spots = []
    video_source = None

    if use_webcam:
        video_source = 0
        parking_spots = load_parking_spots(str(video_source))
        print(parking_spots)
    elif video_file_buffer:
        tfflie = tempfile.NamedTemporaryFile(delete=False)
        tfflie.write(video_file_buffer.read())
        video_source = tfflie.name
        parking_spots = load_parking_spots(video_file_buffer.name)
    else:
        video_source = DEMO_VIDEO
        parking_spots = load_parking_spots(DEMO_VIDEO)

    stop_button = st.sidebar.button('Stop Processing')
    if stop_button:
        st.stop()

    show_boxes = st.sidebar.checkbox('Show Vehicle Bounding Boxes', value=False)
    
    col1, col2, col3 = st.columns([8, 1, 3])
    with col1:
        stframe = st.empty()

    with col3:
        counter_display = st.empty()

    run_parking_detection(
        video_source=video_source,
        model_path=model_path,
        parking_spots=parking_spots,
        stframe=stframe,
        show_boxes=show_boxes,
        counter_display=counter_display
    )

    st.success('Processing complete')

# def parking_page():
#     use_webcam = st.sidebar.button('Use Webcam')
#     video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])

#     model_path = "apps/parking/models/vehicle_detector.pt"
#     parking_spots = []
#     video_source = None

#     if use_webcam:
#         video_source = 0
#         parking_spots = load_parking_spots(str(video_source))
#         print(parking_spots)
#     elif video_file_buffer:
#         tfflie = tempfile.NamedTemporaryFile(delete=False)
#         tfflie.write(video_file_buffer.read())
#         video_source = tfflie.name
#         parking_spots = load_parking_spots(video_file_buffer.name)
#     else:
#         video_source = DEMO_VIDEO
#         parking_spots = load_parking_spots(DEMO_VIDEO)

#     stop_button = st.sidebar.button('Stop Processing')
#     if stop_button:
#         st.stop()

#     show_boxes = st.sidebar.checkbox('Show Vehicle Bounding Boxes', value=False)
    
#     col1, col2, col3 = st.columns([8, 1, 1], gap="small", vertical_alignment="bottom")
#     with col1:
#         stframe = st.empty()

#     with col3:
#         st.write("YES")

#     run_parking_detection(
#         video_source=video_source,
#         model_path=model_path,
#         parking_spots=parking_spots,
#         stframe=stframe,
#         show_boxes=show_boxes
#     )

#     st.success('Processing complete')