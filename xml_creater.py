import requests
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime

# Flask Server Configuration
SERVER_URL = "http://192.168.223.247:5000/logs"
#XML_FILE = "traffic_logs.xml"
XML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traffic_logs.xml")


def create_xml():
    """Creates the base XML structure if the file doesn't exist."""
    root = ET.Element("TrafficLogs")
    tree = ET.ElementTree(root)
    tree.write(XML_FILE, encoding="UTF-8", xml_declaration=True)


def prettify_xml(tree):
    """Formats XML with proper indentation."""
    rough_string = ET.tostring(tree.getroot(), encoding="UTF-8")
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def append_to_xml(log_message):
    """Appends formatted log messages to the XML file."""
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        create_xml()
        tree = ET.parse(XML_FILE)
        root = tree.getroot()

    entry = ET.SubElement(root, "LogEntry")
    timestamp = ET.SubElement(entry, "Timestamp")
    timestamp.text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = ET.SubElement(entry, "Message")
    message.text = log_message

    # Save with pretty formatting
    with open(XML_FILE, "w", encoding="UTF-8") as f:
        f.write(prettify_xml(tree))

    print(f"✅ Log saved: {log_message}")


def listen_to_logs():
    """Continuously listens for server logs and stores them."""
    try:
        with requests.get(SERVER_URL, stream=True) as response:
            response.raise_for_status()  # Raise error if request fails
            for line in response.iter_lines():
                if line:
                    log_message = line.decode("utf-8").replace("data: ", "")
                    print(f"📥 Received log: {log_message}")  # Debugging log
                    append_to_xml(log_message)
    except requests.RequestException as e:
        print(f"❌ Error connecting to server: {e}")


if __name__ == "__main__":
    listen_to_logs()
