import os
import glob

def get_jd_options():
    """Extract job positions from JD filenames"""
    jd_dict = {}
    jd_files = glob.glob("G:/scripts/PG-AGI/hiring-assistant-chatbot/JDs/*")
    
    for file_path in jd_files:
        filename = os.path.basename(file_path)
        # Extract part before '_talenscoutJD'
        if 'talenscout' or 'JD' in filename:
            keys = filename.split('_')
            key="".join(keys[:-2])
            jd_dict[key] = file_path
        else:
            # If no '_talenscoutJD' pattern, use filename without extension
            key = os.path.splitext(filename)[0]
            jd_dict[key] = file_path
    
    return jd_dict



# JDs = get_jd_options()
# print(JDs.keys())