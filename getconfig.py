import datetime
from sshInfo import load_devices
from napalm import get_network_driver

def iso_timestamp():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def get_running_config(device_params):
    driver = get_network_driver("ios")
    device = driver(
        hostname=device_params['hostname'],
        username=device_params['username'],
        password=device_params['password'],
        optional_args={'secret': device_params.get('secret')}
    )
    device.open()
    config_response = device.get_config(retrieve='running')
    device.close()
    return config_response['running']

def configs():
    devices = load_devices("sshInfo.json")
    saved_files = []
    for device_name, device_params in devices.items():
        try:
            running_config = get_running_config(device_params)

            timestamp = iso_timestamp()
            filename = f"{device_name}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(running_config)
            saved_files.append(filename)
        
        except Exception as e:
            saved_files.append(f"Error saving {device_name}: {e}")
    
    return saved_files

if __name__ == "__main__":
    main()