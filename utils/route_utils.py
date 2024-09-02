import requests

def construct_osrm_url(start_point, end_point, waypoints):
    """
    Construct the OSRM URL for routing with given start, end, and waypoints.
    """
    coordinates = [start_point] + waypoints + [end_point]
    coordinates_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    return f"http://router.project-osrm.org/trip/v1/driving/{coordinates_str}?overview=full&geometries=geojson&steps=true&source=first&destination=last&roundtrip=false"

def get_trip_data(osrm_url):
    """
    Get trip data from the OSRM API.
    """
    response = requests.get(osrm_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to get the trip.")