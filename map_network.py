import psutil
import pandas as pd
import requests
from tqdm import tqdm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def get_connection_status(status):
    status_map = {
        psutil.CONN_ESTABLISHED: "ESTABLISHED",
        psutil.CONN_SYN_SENT: "SYN_SENT",
        psutil.CONN_SYN_RECV: "SYN_RECV",
        psutil.CONN_FIN_WAIT1: "FIN_WAIT1",
        psutil.CONN_FIN_WAIT2: "FIN_WAIT2",
        psutil.CONN_TIME_WAIT: "TIME_WAIT",
        psutil.CONN_CLOSE_WAIT: "CLOSE_WAIT",
        psutil.CONN_LAST_ACK: "LAST_ACK",
        psutil.CONN_LISTEN: "LISTEN",
        psutil.CONN_CLOSING: "CLOSING",
    }
    return status_map.get(status, "UNKNOWN")

def get_active_connections():
    active_connections = psutil.net_connections()
    return active_connections

def get_process_info(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.NoSuchProcess:
        return None

def get_ip_details(foreign_address):
    if foreign_address == "N/A":
        return {}  # Return empty dictionary if foreign address is N/A
    try:
        req = requests.get(f"https://ipinfo.io/{foreign_address}")
        return req.json()
    except Exception as e:
        print(f"Error fetching IP details: {e}")
        return {}

def plot_arc_lines(current_location, foreign_locations):
    # Create a new figure
    fig = plt.figure(figsize=(12, 8))

    # Create a Cartopy map with PlateCarree projection
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Set the extent of the map to show the entire world
    ax.set_global()

    # Add land features to the map with a darker background
    ax.add_feature(cfeature.LAND, facecolor='black')
    ax.add_feature(cfeature.COASTLINE, edgecolor='cyan')
    ax.add_feature(cfeature.OCEAN, edgecolor='#330000')
    ax.add_feature(cfeature.STATES, edgecolor='cyan')
    ax.add_feature(cfeature.BORDERS, edgecolor='cyan')

    # Plot the current location
    ax.plot(current_location[1], current_location[0], 'ro', markersize=10, transform=ccrs.PlateCarree())

    # Plot arc lines for all foreign locations
    for foreign_location in foreign_locations:
        foreign_coords = foreign_location["coords"]
        foreign_label = foreign_location["label"]
        ax.plot([current_location[1], foreign_coords[1]], [current_location[0], foreign_coords[0]], 'g--', transform=ccrs.PlateCarree())
        ax.text(foreign_coords[1], foreign_coords[0], foreign_label, color='white', fontsize=8, ha='left', va='center', transform=ccrs.PlateCarree())
    # Show the map
    plt.show()

def main():
    # Initialize an empty list to store connection data
    data = []

    # Set pandas display options
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    active_connections = get_active_connections()

    total_connections = len(active_connections)

    connection_details = {
        "Local Address": [],
        "Foreign Address": [],
        "hostname": [],
        "org": [],
        "Status": [],
        "Process Name": [],
        "City": [],
        "Region": [],
        "Country": []
    }


    current_location = (8.2503495, 124.2547768)  # Your current location coordinates
    foreign_locations = []

    with tqdm(total=total_connections, desc="Processing Connections") as pbar:
        for connection in active_connections:
            connection_details["Local Address"].append(f"{connection.laddr.ip}:{connection.laddr.port}")
            connection_details["Foreign Address"].append(f"{connection.raddr.ip}:{connection.raddr.port}" if connection.raddr else "N/A")
            connection_details["Status"].append(get_connection_status(connection.status))
            pid = connection.pid
            process_name = get_process_info(pid)
            connection_details["Process Name"].append(process_name if process_name else 'N/A')
            
            ip_details = get_ip_details(connection.raddr.ip if connection.raddr else "N/A")
            city = ip_details.get('city', '')
            region = ip_details.get('region', '')
            country = ip_details.get('country', '')
            hostname = ip_details.get('hostname', '')
            org = ip_details.get('org', '')
            connection_details["hostname"].append(hostname)
            connection_details["org"].append(org)
            connection_details["City"].append(city)
            connection_details["Region"].append(region)
            connection_details["Country"].append(country)
            loc = ip_details.get('loc', '')
            if loc:
                lat, lon = map(float, loc.split(','))
                # foreign_locations.append((lat, lon))
                label_text = f"{city}, {region}, {country}"
                foreign_locations.append({
                    "coords" : (lat, lon),
                    "label" : label_text
                })
            pbar.update(1)  # Update progress bar
        df = pd.DataFrame(connection_details)
        print("Active Connections Details:")
        print(df)

    # Plot arc lines on the world map
    plot_arc_lines(current_location, foreign_locations)

if __name__ == "__main__":
    main()
