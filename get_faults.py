import requests
import urllib3
import json

# Disable warnings for self-signed certificates (optional)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def query_apic_faultinfo_to_file(apic_host, username, password, output_file="faultinfo.json"):
    """
    Query the Cisco APIC REST API to get fault information and save it to a JSON file.

    Args:
        apic_host (str): The APIC IP address or hostname (e.g., '10.0.0.1' or 'apic.example.com')
        username (str): APIC username
        password (str): APIC password
        output_file (str): Filename to save the JSON output (default: 'faultinfo.json')

    Returns:
        bool: True if successful, False otherwise
    """
    base_url = f"https://{apic_host}"
    login_url = f"{base_url}/api/aaaLogin.json"
    login_payload = {
        "aaaUser": {
            "attributes": {
                "name": username,
                "pwd": password
            }
        }
    }

    session = requests.Session()

    try:
        # Authenticate to APIC and get token cookie
        login_response = session.post(login_url, json=login_payload, verify=False)
        login_response.raise_for_status()

        # Query the faultinfo class
        faultinfo_url = f"{base_url}/api/class/faultInfo.json"
        response = session.get(faultinfo_url, verify=False)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Write JSON data to file with indentation for readability
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Fault information saved to {output_file}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error querying APIC: {e}")
        return False

# Example usage:
if __name__ == "__main__":
    apic = "apic.example.com"
    user = "xxxxx"
    pwd = "pppppppp"
    success = query_apic_faultinfo_to_file(apic, user, pwd)
    if success:
        print("Query and file write completed successfully.")