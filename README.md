# Automated OSPF Configuration Manager

This project provides a web-based, automated approach to managing, configuring, and migrating Cisco IOS devices. Built with Python and Flask, it leverages NAPALM to interact directly with network hardware, offering a centralized dashboard for OSPF deployment, configuration backups, difference tracking, and automated failover testing.

## Features

* **Web UI Management**: A Flask application serves as the frontend dashboard to manage network operations seamlessly.
* **Database Integration**: Utilizes SQLite to securely store and retrieve router configurations, credentials, and OSPF parameters.
* **Automated Configuration Backups**: Connects to the device inventory to fetch and save running configurations with standardized ISO timestamps.
* **Configuration Auditing**: Compares the current running configuration on a device against the latest backup, outputting a unified diff to highlight changes.
* **Dynamic OSPF Deployment**: Programmatically pushes specific OSPF configurations to routers based on their role in the topology (e.g., Area 0, Area 1, or split areas for load balancing).
* **IPv4 Validation**: Features built-in logic to strictly validate IPv4 addresses, ensuring loopbacks, broadcast, multicast, and reserved IPs are filtered out before deployment.
* **Automated Connectivity Testing**: Initiates automated ping sweeps from designated routers (e.g., R1) to verify network reachability and OSPF convergence.
* **Live Migration Execution**: Automates a graceful network migration by manipulating OSPF costs to failover traffic, applying maintenance banners, and utilizing background threads to continuously monitor packet loss during the transition.
* **Centralized Inventory**: Device credentials and host IPs are securely loaded from a central JSON inventory file.

## Project Structure

* `lab4main.py`: The core Flask application defining all web routes and tying the modules together.
* `database.py`: Handles SQLite database initialization and data transactions.
* `getconfig.py`: Extracts and backs up running configurations using NAPALM.
* `diffconfig.py`: Performs diff operations between saved and active configurations.
* `ospfconfig.py`: Manages the OSPF area logic, commits configurations to the devices, and verifies post-deployment connectivity.
* `migration.py`: Orchestrates a multi-step failover process, including link manipulation and continuous background pinging to measure downtime.
* `connectivity.py`: Contains the logic to ping target loopback IPs across the topology.
* `validateIPv4.py`: A utility script for rigorous IP address validation.
* `sshInfo.json` / `sshInfo.py`: Stores and loads the target device inventory.
* `templates/`: Directory containing all Flask HTML templates for the frontend web UI.
  * `index.html`: The main landing page for the application.
  * `get_config.html`: Displays the results and filenames of successfully backed-up configurations.
  * `ospf_home.html`: The main dashboard page for OSPF management.
  * `ospf_form.html`: Provides the input form for defining OSPF process IDs, areas, and loopback IPs for a specific router.
  * `ospf_results.html`: Shows the deployment status and connectivity validation table after pushing OSPF configs.
  * `diff_results.html`: Renders the unified diff output comparing running and backed-up configurations.
  * `migration_results.html`: Displays the execution logs and ping statistics from the automated failover migration.

## Prerequisites

To run this project, ensure you have the following installed:
* Python 3.x
* Flask
* NAPALM
* PrettyTable
* SSH connectivity to routers

## Usage

1. **Initialize the Environment**: Ensure `sshInfo.json` is updated with your target router IPs and credentials.
2. **Start the Web Server**: Run the main Flask application:
   ```bash
   python3 lab4main.py
   ```
3. **Access the Dashboard**: Navigate to `http://localhost:80` (or your server's IP) in your web browser.
4. **Deploy & Manage**: Use the UI to back up configurations, define OSPF parameters, push changes to the network, or run the automated migration script.
