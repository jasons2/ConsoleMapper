# Mapit - Overview

An automation utility for auditing **Cisco Terminal Servers** (Access Servers) to map physical async ports to the actual devices connected to them. 

This tool eliminates the manual guesswork of "which console cable goes where" by programmatically crawling every line and documenting the downstream environment.

## 🚀 The Workflow
1. **Line Discovery:** Connects to the Terminal Server via CLI to parse `show line` output.
2. **Dynamic Mapping:** Calculates the [Reverse Telnet](https://www.cisco.com) ports using the `2000 + Line Number` convention.
3. **Automated Handshake:** Iterates through each port, sends a carriage return to wake the console, and captures the device hostname.
4. **Structured Export:** Compiles all discovered data into a clean `.csv` file for inventory management.

## 🛠 Features
*   **Zero Hardcoding:** Automatically detects which lines are asynchronous vs. VTY or Console.
*   **Session Management:** Gracefully handles connections and ensures lines are cleared after polling.
*   **Port Logic:** Supports standard Cisco base-2000 addressing for individual line access.
*   **Audit-Ready:** Generates a mapping of `Line ID -> Port Number -> Hostname`.

## 📋 Requirements
* **Terminal Server Config:** Lines must be configured with `transport input telnet` (or `all`).
* **Connectivity:** Network reachability to the Terminal Server's loopback or management IP.
* **Environment:** Python 3.x with `Netmiko` or `Paramiko` (suggested for CLI interaction).

## 📖 Sample Output
The tool produces a `terminal_server_map.csv` formatted like this:


| Terminal Server | Line | Port | Connected Hostname |
| :--- | :--- | :--- | :--- |
| TS-CORE-01 | 1 | 2001 | Edge-Router-A |
| TS-CORE-01 | 2 | 2002 | Switch-Floor-02 |
| TS-CORE-01 | 3 | 2003 | Firewall-Primary |

## ⚠️ Known Limitations
* **Occupied Lines:** If a line is currently in use by another user, the tool will mark the device as `BUSY` or `UNREACHABLE`.
* **Standard Ports:** Uses the default `2000` base; if your server uses custom rotary groups (base `3000`), port offsets may vary.

---
*Maintained by [Your Name/Handle]*
# Usage
<pre>
usage: mapit.py [-h] -u USERNAME [-p PASSWORD] -l LOOPBACK -t TERMSERV_IP_ADDRESS -c CSV_FILE_NAME

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        username
  -p PASSWORD, --password PASSWORD
                        password (prompted safely on the CLI if not given)
  -l LOOPBACK, --loopback LOOPBACK
                        Loopback IP Address
  -t TERMSERV_IP_ADDRESS, --termserv_ip_address TERMSERV_IP_ADDRESS
                        IP address of terminal server
  -c CSV_FILE_NAME, --csv_file_name CSV_FILE_NAME
                        Filename for CSV file to be created

Example:
mapit.py -u 'some_user' -p 'somepass' -l '10.10.10.10' -t '192.168.1.1' -c 'output_file.csv'
</pre>


# Example Output
<pre>
TTY,Port,Hostname
1/0,2066,SomeHostname
1/1,2067,AnotherHostName
1/2,2068,AThirdHostName  
</pre>


---
*Maintained by [Jason Smith]*
