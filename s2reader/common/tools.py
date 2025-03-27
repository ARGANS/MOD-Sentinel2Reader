import xml.etree.ElementTree as ET
from pathlib import Path

def read_xml(xml_path:Path) -> ET.ElementTree:
    """ Read an XML file and return the parsed data

    Args:
        xml_path (Path): Filepath to the XML file

    Returns:
        ET.ElementTree: Parsed XML data
    """
    
    tree = ET.parse(str(xml_path))
    return tree