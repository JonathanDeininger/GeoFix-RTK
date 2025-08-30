import csv
import sys
import os
from datetime import datetime

def create_kml_from_csv(input_file, output_file=None):
    """
    Convert coordinates CSV to KML file.
    
    Args:
        input_file: Path to the coordinates CSV file
        output_file: Optional output file name (defaults to input_file.kml)
    """
    try:
        coordinates = []
        
        # Read the CSV file
        with open(input_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                lat = row.get('Latitude', '').strip()
                lon = row.get('Longitude', '').strip()
                
                if lat and lon:
                    coordinates.append((float(lon), float(lat)))  # KML uses lon,lat order
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.kml"
        
        # Create KML content
        kml_content = create_kml_content(coordinates, os.path.basename(input_file))
        
        # Save to KML file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(kml_content)
        
        print(f"Converted {len(coordinates)} coordinate pairs to KML")
        print(f"Saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

def create_kml_content(coordinates, source_name):
    """
    Create KML content with both a path and individual points.
    
    Args:
        coordinates: List of (longitude, latitude) tuples
        source_name: Name of the source file for labeling
    
    Returns:
        KML content as string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>GPS Track from {}</name>
    <description>Generated on {}</description>
    
    <Style id="trackStyle">
        <LineStyle>
            <color>ff0000ff</color>
            <width>3</width>
        </LineStyle>
    </Style>
    
    <Style id="pointStyle">
        <IconStyle>
            <color>ff00ff00</color>
            <scale>0.5</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>
            </Icon>
        </IconStyle>
    </Style>'''.format(source_name, timestamp)
    
    # Create path/track
    kml_path = '''
    <Placemark>
        <name>GPS Track</name>
        <description>Complete GPS track path</description>
        <styleUrl>#trackStyle</styleUrl>
        <LineString>
            <tessellate>1</tessellate>
            <coordinates>'''
    
    # Add coordinates to path (lon,lat,altitude format)
    for lon, lat in coordinates:
        kml_path += f"\n                {lon},{lat},0"
    
    kml_path += '''
            </coordinates>
        </LineString>
    </Placemark>'''
    
    # Create individual points (optional - can be commented out if too many points)
    kml_points = ""
    if len(coordinates) <= 50:  # Only add individual points if not too many
        for i, (lon, lat) in enumerate(coordinates):
            kml_points += f'''
    <Placemark>
        <name>Point {i+1}</name>
        <description>Lat: {lat}, Lon: {lon}</description>
        <styleUrl>#pointStyle</styleUrl>
        <Point>
            <coordinates>{lon},{lat},10</coordinates>
        </Point>
    </Placemark>'''
    
    kml_footer = '''
</Document>
</kml>'''
    
    return kml_header + kml_path + kml_points + kml_footer

if __name__ == "__main__":
    # Default input file
    input_file = "gpslog_coordinates.csv"
    
    # Check if file exists
    if os.path.exists(input_file):
        create_kml_from_csv(input_file)
        print("\nThe KML file can be opened in:")
        print("- Google Earth")
        print("- Google Maps (by uploading)")
        print("- Other GIS applications")
    else:
        print(f"File {input_file} not found in current directory")
        print("Usage: python csv_to_kml.py")
