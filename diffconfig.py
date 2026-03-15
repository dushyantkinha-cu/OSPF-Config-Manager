import difflib
import os
import glob
from napalm import get_network_driver
from sshInfo import load_devices
from getconfig import get_running_config

def get_latest_backup(hostname):
    # This looks for the config files starting with R1_, R2_, etc..
    files = glob.glob(f"{hostname}_*.txt")
    if not files:
        return None
    files.sort()
    return files[-1]    

def get_diffs():
    devices = load_devices("sshInfo.json")
    diff_results = []

    for device_name, params in devices.items():
        try:
            latest_file = get_latest_backup(device_name)
            if not latest_file:
                diff_results.append({"device": device_name,"status": "Error", "output": "No backup file found. Please run 'Get Config' first."})
                continue

            with open(latest_file, 'r') as f:
                old_config_lines = f.readlines()

            # This fetches the current running config from the device and splits them into a single line
            new_config_raw = get_running_config(params)
            new_config_lines = new_config_raw.splitlines(keepends=True)
            
            # difflib.unified_diff gets the difference in config between two lists of strings
            diff = difflib.unified_diff(
                old_config_lines, 
                new_config_lines, 
                fromfile=f"Backup ({latest_file})", 
                tofile="Current Running Config"
            )
            
            diff_text = "".join(diff)

            if not diff_text:
                diff_text = "No changes detected (Configurations are identical)."

            diff_results.append({
                "device": device_name,
                "status": "Success",
                "output": diff_text
            })

        except Exception as e:
            diff_results.append({
                "device": device_name,
                "status": "Error",
                "output": str(e)
            })

    return diff_results