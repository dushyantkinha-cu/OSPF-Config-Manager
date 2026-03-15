import sqlite3

def init_db():
    # This initializes the SQLite database with the required schema
    conn = sqlite3.connect("network_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS routers
                 (hostname TEXT PRIMARY KEY, 
                  username TEXT, 
                  password TEXT, 
                  ospf_process_id TEXT, 
                  ospf_area_id TEXT, 
                  ospf_area_id_2 TEXT,
                  loopback_ip TEXT)''')
    conn.commit()
    conn.close()

def save_router_data(data):
    # This saves and/or updates router configurations in the database
    conn = sqlite3.connect("network_data.db")
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO routers 
                 (hostname, username, password, ospf_process_id, ospf_area_id, ospf_area_id_2, loopback_ip) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                 (data['hostname'], data['username'], data['password'], 
                  data['ospf_process'], data['ospf_area'], data.get('ospf_area_2', ''), data['loopback_ip']))
    conn.commit()
    conn.close()

def get_all_routers():
    # This retrieves router information from the database
    conn = sqlite3.connect("network_data.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM routers")
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    main()