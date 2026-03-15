import time
import threading
from napalm import get_network_driver
from sshInfo import load_devices

# This defines a global event to control the continous ping loop
stop_ping_event = threading.Event()

def continuous_ping_worker(devices, ping_results):
    # This will initiate a continous ping from R1_Kinha to R3_Kinha's Loopback IP
    r1_params = devices['R1_Kinha']
    driver = get_network_driver("ios")
    r1 = driver(
        hostname=r1_params['hostname'], 
        username=r1_params['username'], 
        password=r1_params['password'],
        optional_args={'secret': r1_params['password'], 'global_delay_factor': 2})
    
    try:
        r1.open()
        target = "30.0.0.1"
        sequence = 1
        while not stop_ping_event.is_set():
            # This pings with a short delay to be responsive
            ping = r1.ping(target, count=1)
            timestamp = time.strftime("%H:%M:%S")
            if ping['success']['packet_loss'] == 0:
                ping_results.append(f"[{timestamp}] Seq={sequence} Ping R1->R3: SUCCESS")
            else:
                ping_results.append(f"[{timestamp}] Seq={sequence} Ping R1->R3: FAIL (DROP!)")
            sequence += 1
            time.sleep(1)        
        r1.close()
    
    except Exception as e:
        ping_results.append(f"Background Ping Error: {str(e)}")

def run_migration():
    logs = []
    ping_logs = []
    devices = load_devices("sshInfo.json")
    r4_params = devices['R4_Kinha']
    
    logs.append("Starting continuous background ping (R1 -> R3)...")
    stop_ping_event.clear() # Resetting the stop flag
    # This creates the thread for continous ping
    ping_thread = threading.Thread(target=continuous_ping_worker, args=(devices, ping_logs,))
    ping_thread.start()
    time.sleep(5)
    
    try:
        driver = get_network_driver("ios")
        r4 = driver(
            hostname=r4_params['hostname'], 
            username=r4_params['username'], 
            password=r4_params['password'],
            optional_args={'secret': r4_params['password'], 'global_delay_factor': 2, 'inline_transfer': True}
        )
        r4.open()
        
        # This is the interface on R4_Kinha facing SW2
        target_interface = "FastEthernet0/0"
        
        # Increasing cost on R4_Kinha so traffic prefers R2_Kinha
        logs.append("Initiating OSPF Cost-Out to fail over all the traffic to R2_Kinha")
        config_cost_out = [f"interface {target_interface}", "ip ospf cost 65535"]
        r4.load_merge_candidate(config='\n'.join(config_cost_out))
        r4.commit_config()
        logs.append("Cost applied. Waiting 15s for OSPF convergence.")
        time.sleep(15)

        # Checking Traffic Counters on the link b/w R4_Kinha and SW2
        counters = r4.get_interfaces_counters()[target_interface]
        logs.append(f"Traffic Check on {target_interface}: Tx={counters['tx_unicast_packets']} / Rx={counters['rx_unicast_packets']}")
          
        # This shuts down the inteface on R2_Kinha facing SW2
        logs.append(f"Shutting down {target_interface} on R4...")
        config_shutdown = [f"interface {target_interface}", "shutdown"]
        r4.load_merge_candidate(config='\n'.join(config_shutdown))
        r4.commit_config()
        logs.append("R4 Interface is now DOWN.")
        logs.append("Traffic should now be flowing via R2_Kinha")

        # This will configure a banner on R4_Kinha
        logs.append("Applying Maintenance Banner...")
        config_banner = ["banner motd #Change made for migration in Lab 4#"]
        r4.load_merge_candidate(config='\n'.join(config_banner))
        r4.commit_config()
        
        # This will bring the interface UP and revert the ospf cost
        logs.append(f"Restoring {target_interface} on R4...")
        config_restore = [f"interface {target_interface}", "no shutdown", "no ip ospf cost"]
        r4.load_merge_candidate(config='\n'.join(config_restore))
        r4.commit_config()
        
        # This gives OSPF a moment to converge
        logs.append("Waiting 15 seconds for OSPF convergence")
        time.sleep(15)
        r4.close()

    except Exception as e:
        logs.append(f"Critical Error during migration: {str(e)}")
    
    finally:
        logs.append("Stopping background pings...")
        stop_ping_event.set() # Tells the thread to stop
        ping_thread.join()    # Waits for the thread to finish cleanly
        
        logs.append("\n--- CONTINUOUS PING REPORT ---")
        logs.extend(ping_logs)
        logs.append("Migration completed successfully")

    return logs