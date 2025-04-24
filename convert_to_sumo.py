import xml.etree.ElementTree as ET
import xml.dom.minidom
import random
import os

# File Paths
TRAFFIC_LOGS_FILE = "traffic_logs.xml"
SUMO_ROUTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "new_routes.rou.xml")

# Define vehicle types and their SUMO attributes
VEHICLE_TYPES = {
    "Car": "car",
    "Bike": "bike",
    "Truck": "truck",
    "Ambulance": "ambulance"
}

SUMO_VEHICLE_ATTRIBUTES = {
    "car": {"accel": "1.0", "decel": "4.5", "sigma": "0.5", "length": "5.0", "minGap": "2.5", "maxSpeed": "13.89", "guiShape": "passenger"},
    "bike": {"accel": "1.5", "decel": "4.5", "sigma": "0.5", "length": "2.0", "minGap": "1.0", "maxSpeed": "10.0", "guiShape": "motorcycle"},
    "truck": {"accel": "0.8", "decel": "4.5", "sigma": "0.5", "length": "10.0", "minGap": "3.0", "maxSpeed": "10.0", "guiShape": "truck"},
    "ambulance": {"accel": "1.2", "decel": "4.5", "sigma": "0.5", "length": "5.0", "minGap": "2.5", "maxSpeed": "25.0", "guiShape": "emergency"}
}

# Define SUMO-compatible routes
SUMO_ROUTES = {
    "route0": "-E6 -E1 -E0",
    "route1": "E0 E1 E6",
    "route2": "-E6 -E1 -E0",
    "route3": "E0 E1 E6",
    "route4": "-E6 -E1 -E0",
    "route5": "E0 E1 E6",
    "route6": "-E6 -E1 -E0",
    "route7": "E0 E1 E6"
}

def safe_eval(data_str):
    """Safely parses dictionary-like strings."""
    try:
        data = eval(data_str, {"__builtins__": None}, {})
        return data if isinstance(data, dict) else None
    except:
        return None

def parse_traffic_logs():
    """Parses traffic_logs.xml and extracts vehicle information."""
    try:
        tree = ET.parse(TRAFFIC_LOGS_FILE)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        print("❌ Error: Traffic logs XML file is missing or corrupt!")
        return {}

    vehicles = {}

    for entry in root.findall("LogEntry"):
        message_elem = entry.find("Message")
        if message_elem is None or "MAC:" not in message_elem.text:
            continue

        message = message_elem.text
        parts = message.split("→")
        if len(parts) < 2:
            continue

        mac_address = parts[0].split(":")[-1].strip()
        details = safe_eval(parts[1].strip())

        if details:
            vehicle_type = VEHICLE_TYPES.get(details.get("type", "Car"), "car")
            vehicles[mac_address] = {
                "type": vehicle_type,
                "route": random.choice(list(SUMO_ROUTES.keys())),
                "depart": random.randint(0, 30)
            }
        else:
            print(f"⚠️ Error parsing vehicle details: {message}")

    return vehicles

def prettify_xml(tree):
    """Formats XML with proper indentation."""
    rough_string = ET.tostring(tree.getroot(), encoding="UTF-8")
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_sumo_xml(vehicles):
    """Generates SUMO XML file from extracted traffic log data."""
    root = ET.Element("routes", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd"
    })

    # Define vehicle types
    for vtype, attributes in SUMO_VEHICLE_ATTRIBUTES.items():
        ET.SubElement(root, "vType", {"id": vtype, **attributes})

    # Define routes
    for route_id, edges in SUMO_ROUTES.items():
        ET.SubElement(root, "route", {"id": route_id, "edges": edges})

    # ✅ Sort vehicles by departure time
    sorted_vehicles = sorted(vehicles.items(), key=lambda item: item[1]["depart"])

    # Add vehicle entries
    for mac, data in sorted_vehicles:
        vehicle_id = f"vehicle_{mac.replace(':', '_')}"
        vehicle_attributes = {
            "id": vehicle_id,
            "type": data["type"],
            "route": data["route"],
            "depart": str(data["depart"])
        }
        if data["type"] == "ambulance":
            vehicle_attributes["color"] = "1,0,0"
        ET.SubElement(root, "vehicle", vehicle_attributes)

    # Save the XML
    with open(SUMO_ROUTES_FILE, "w", encoding="UTF-8") as f:
        f.write(prettify_xml(ET.ElementTree(root)))

    print(f"✅ SUMO XML generated: {SUMO_ROUTES_FILE}")

if __name__ == "__main__":
    vehicles = parse_traffic_logs()
    if vehicles:
        generate_sumo_xml(vehicles)
    else:
        print("⚠️ No valid vehicle data found in logs.")
