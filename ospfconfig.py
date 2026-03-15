import time
import ipaddress
from validateIPv4 import valid_ipv4
from prettytable import PrettyTable
from database import get_all_routers
from napalm import get_network_driver
from connectivity import ping_from_router

def configure_network():
    routers = get_all_routers()
    results = []
    
    # This prints out PrettyTable IP Validation block
    pt = PrettyTable()
    pt.field_names = ["Router", "Loopback IP", "Syntax Valid", "Configured on Device"]

    for r in routers:
        status_msg = ""
        try:
            driver = get_network_driver('ios')
            device = driver(hostname=r['hostname'], username=r['username'], password=r['password'], optional_args={ 'secret': r['password']})
            device.open()

            # This checks if the Loopback IP exists on the device
            interfaces_ip = device.get_interfaces_ip()
            is_configured = "No"
            target_ip = r['loopback_ip'].split('/')[0]
            is_valid_syntax = valid_ipv4(target_ip)
            
            for intf, ips in interfaces_ip.items():
                if target_ip in ips.get('ipv4', {}):
                    is_configured = "Yes"
            
            # A valid syntax & Loopback IP status is updated to the table
            pt.add_row([r['hostname'], r['loopback_ip'], is_valid_syntax, is_configured])

            # OSPF Configuration logic
            ospf_commands = [f"router ospf {r['ospf_process_id']}",
                             f" router-id {target_ip}"]
            
            # R1 should only be Area 1, so the appropriate commands are appended
            if "198.51.100.1" in r['hostname']:
                ospf_commands.append(f" network 0.0.0.0 255.255.255.255 area {r['ospf_area_id']}")
            # R3 should only be Area 0, so the appropriate commands are appended
            elif "172.16.1.3" in r['hostname']:
                 ospf_commands.append(f" network 0.0.0.0 255.255.255.255 area {r['ospf_area_id']}")
            # R2 and R4 should do equal-cost load balancing, meaning - Split Areas
            elif "198.51.101.2" in r['hostname'] or "198.51.101.4" in r['hostname']:
                # This is for interface facing R1 (198.51.101.0/24) which goes to Area 1 (ospf_area_id_2)
                ospf_commands.append(f" network 198.51.101.0 0.0.0.255 area {r['ospf_area_id_2']}")
                # This is for interface facing R3 (172.16.1.0/24) which goes to Area 0 (ospf_area_id)
                ospf_commands.append(f" network 172.16.1.0 0.0.0.255 area {r['ospf_area_id']}")
                # This is for Loopback and it goes to Area 0
                ospf_commands.append(f" network {target_ip} 0.0.0.0 area {r['ospf_area_id']}")
            
            # This joins the OSPF commands and applies the config
            device.load_merge_candidate(config='\n'.join(ospf_commands))
            device.commit_config()
            device.close()
            status_msg = f"Configured {r['hostname']} successfully."

        except Exception as e:
            status_msg = f"Error on {r['hostname']}: {str(e)}"
        
        results.append(status_msg)

    # This prints a table on the server console
    print("\n" + str(pt))
    
    # This waits 60s for OSPF to converge and pings all the Loopback IPs from R1_Kinha
    print("\nWaiting 60 seconds for OSPF to converge...")
    time.sleep(60)
    ping_results = ping_from_router()
    results.extend(ping_results)
    
    return results

if __name__ == "__main__":
    main()