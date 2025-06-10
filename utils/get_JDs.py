import os
import glob

def get_jd_options():
    """Extract job positions from JD filenames"""
    jd_dict = {}

    # Get the path to the current script (e.g., utils/)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Move up one level to the main app folder
    app_dir = os.path.dirname(base_dir)

    # Construct the path to the JDs folder
    jd_folder = os.path.join(app_dir, "JDs")

    # Get all files inside JDs
    jd_files = glob.glob(os.path.join(jd_folder, "*"))

    for file_path in jd_files:
        filename = os.path.basename(file_path)
        # Extract part before '_talenscoutJD'
        if 'talenscout' in filename or 'JD' in filename:
            keys = filename.split('_')
            key = "".join(keys[:-2]) if len(keys) >= 2 else filename
            jd_dict[key] = file_path
        else:
            # If no '_talenscoutJD' pattern, use filename without extension
            key = os.path.splitext(filename)[0]
            jd_dict[key] = file_path
    
    return jd_dict
