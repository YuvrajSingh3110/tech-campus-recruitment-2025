import sys
import os
import zipfile
from datetime import datetime
import gdown
import io

def download_from_gdrive(file_id, output_path):
    """
    Downloads a file from Google Drive if it doesn't exist locally.

    """
    if os.path.exists(output_path):
        print(f"Zip file already exists at {output_path}")
        return
        
    print(f"Downloading log file from Google Drive...")
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, output_path, quiet=False)
    print("Download complete!")

def process_zip_content(zip_path, target_date, output_file, chunk_size=1024*1024):
    """
    Process zip file content directly without full extraction.
    """
    print(f"Processing logs for {target_date}...")
    lines_processed = 0
    matches_found = 0
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get the first file in the zip
        log_filename = zip_ref.namelist()[0]
        with zip_ref.open(log_filename) as log_file, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            # Process the file in chunks
            buffer = ""
            while True:
                chunk = log_file.read(chunk_size)
                if not chunk:
                    break
                
                # Decode chunk and add to buffer
                buffer += chunk.decode('utf-8', errors='ignore')
                
                # Process complete lines
                lines = buffer.split('\n')
                # Keep the last partial line in buffer
                buffer = lines[-1]
                
                # Process all complete lines
                for line in lines[:-1]:
                    lines_processed += 1
                    if line.startswith(target_date):
                        outfile.write(line + '\n')
                        matches_found += 1
                    
                    if lines_processed % 1000000 == 0:
                        print(f"Processed {lines_processed:,} lines... Found {matches_found:,} matches")
            
            # Process any remaining content in buffer
            if buffer and buffer.startswith(target_date):
                outfile.write(buffer)
                matches_found += 1

    print(f"Completed! Processed {lines_processed:,} lines and found {matches_found:,} matches")
    return matches_found

def extract_logs(target_date, output_dir=None):
    """
    Extracts logs for the specified date and writes them to an output file.

    Parameters:
    target_date (str): Date in YYYY-MM-DD format.
    output_dir (str): Directory to save the extracted logs.
    """
    # Get the script's directory and navigate up one level to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Set output directory relative to project root
    output_dir = os.path.join(project_root, "output")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download zip file from Google Drive
    zip_path = os.path.join(output_dir, "logs.zip")
    file_id = "1kQPeECKHD4_x_1f9qKjzCSo0MKvxik_2"
    download_from_gdrive(file_id, zip_path)
    
    # Process the zip file directly
    output_file = os.path.join(output_dir, f"output_{target_date}.txt")
    try:
        matches = process_zip_content(zip_path, target_date, output_file)
        if matches > 0:
            print(f"Logs for {target_date} extracted successfully to {output_file}")
        else:
            print(f"No logs found for date {target_date}")
    
    except FileNotFoundError:
        print("Error: Zip file not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_logs.py <YYYY-MM-DD>")
        sys.exit(1)
    
    date = sys.argv[1]
    extract_logs(date)