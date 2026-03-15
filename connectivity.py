from napalm import get_network_driver
from database import get_all_routers

def ping_from_router():
    routers = get_all_routers()
    results = []
    
    # This extracts R1_Kinha details from the database
    r1 = None
    for r in routers:
        if '198.51.100.1' in r['hostname']:
            r1 = r
            break

    driver = get_network_driver("ios")
    device = driver(hostname=r1['hostname'], 
                    username=r1['username'], 
                    password=r1['password'],
                    optional_args={ 'secret': r1['password'],
                    'global_delay_factor': 4})
    device.open()
    
    for target in routers:
        # This removes the subnet mask. Eg: Converts '10.0.0.1/32' -> '10.0.0.1')
        target_ip = target['loopback_ip'].split('/')[0]
        
        # This pings each Loopback IP from R1_Kinha
        ping_response = device.ping(target_ip, count=2)
        if ping_response['success']['packet_loss'] == 0:
            results.append(f"Ping to {target['hostname']} ({target_ip}): SUCCESS")
        else:
            results.append(f"Ping to {target['hostname']} ({target_ip}): FAIL")
    
    device.close()
    return results

if __name__ == "__main__":
    main()