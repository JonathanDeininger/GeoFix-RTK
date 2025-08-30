import csv
import sys
import os

def extract_coordinates(input_file, output_file=None):
    """
    Extract latitude and longitude from GPS log file.
    
    Args:
        input_file: Path to the GPS log CSV file
        output_file: Optional output file name (defaults to input_file_coordinates.csv)
    """
    try:
        coordinates = []
        valid_rows = 0
        total_rows = 0
        
        # Read the CSV file
        with open(input_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                total_rows += 1
                
                # Filter out rows with empty Fix_Status or 'Unbekannt'
                fix_status = row.get('Fix_Status', '').strip()
                fix_description = row.get('Fix_Description', '').strip()
                
                if fix_status and fix_status != '' and fix_description != 'Unbekannt':
                    lat = row.get('Latitude', '').strip()
                    lon = row.get('Longitude', '').strip()
                    
                    if lat and lon:
                        coord_pair = (lat, lon)
                        if coord_pair not in coordinates:  # Simple duplicate removal
                            coordinates.append(coord_pair)
                        valid_rows += 1
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_coordinates.csv"
        
        # Save to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Latitude', 'Longitude'])  # Header
            writer.writerows(coordinates)
        
        print(f"Extracted {len(coordinates)} unique coordinate pairs")
        print(f"Saved to: {output_file}")
        print(f"Original file had {total_rows} rows, filtered to {valid_rows} valid GPS fixes")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Default input file
    input_file = "gpslog.csv"
    
    # Check if file exists
    if os.path.exists(input_file):
        extract_coordinates(input_file)
    else:
        print(f"File {input_file} not found in current directory")
        print("Usage: python extract_coordinates.py")
