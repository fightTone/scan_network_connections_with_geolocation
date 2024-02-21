import psutil
import pandas as pd
import requests
from tqdm import tqdm

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

def main():
    # Set pandas display options
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    active_connections = get_active_connections()

    data = []
    total_connections = len(active_connections)

    with tqdm(total=total_connections, desc="Processing Connections") as pbar:
        for connection in active_connections:
            protocol = connection.type
            local_address = f"{connection.laddr.ip}:{connection.laddr.port}"
            foreign_address = f"{connection.raddr.ip}:{connection.raddr.port}" if connection.raddr else "N/A"
            status = get_connection_status(connection.status)
            pid = connection.pid
            process_name = get_process_info(pid)
            
            ip_details = get_ip_details(connection.raddr.ip if connection.raddr else "N/A")
            city = ip_details.get('city', '')
            region = ip_details.get('region', '')
            country = ip_details.get('country', '')
            loc = ip_details.get('loc', '')
            org = ip_details.get('org', '')
            postal = ip_details.get('postal', '')
            timezone = ip_details.get('timezone', '')
            readme = ip_details.get('readme', '')

            if process_name:
                data.append([protocol, local_address, foreign_address, status, pid, process_name, city, region, country, loc, org, postal, timezone, readme])
            else:
                data.append([protocol, local_address, foreign_address, status, pid, "N/A", city, region, country, loc, org, postal, timezone, readme])

            pbar.update(1)  # Update progress bar

    columns = ["Protocol", "Local Address", "Foreign Address", "Status", "PID", "Process Name", "City", "Region", "Country", "Location", "Organization", "Postal", "Timezone", "Readme"]
    df = pd.DataFrame(data, columns=columns)

    # Sort the DataFrame by process name
    df.sort_values(by="Process Name", inplace=True)

    print(df)

if __name__ == "__main__":
    main()
