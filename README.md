# rfa-ansible


# Orion Dynamic Inventory Component
**Expected Output**
* host groups defining tenancy, based on the orion "Orion.NodesCustomProperties.CustomerName" db field.
* host names describing device ip, based on the orion "Orion.Nodes.IPAddress" db field.
* group vars defining org id, based on the orion "Orion.NodesCustomProperties.CWID" db field.
* host vars cateogrizing the device type, based on the orion "Orion.Nodes.NodeDescription" db field.

**Generating the Credential File**
1. create a dir titled "creds" in the same directory as the orion-inventory.py file
2. create a file in "./creds/" titled "orion_creds.py"
3. populate this file with the following content
        ```
        username = "USERNAMEHERE"
        password = "PASSWORDHERE"
        server = "ORIONHOSTIPHERE"
        ```
        
**Running the Inventory in Python**
1. call the python python executable with the absolute or relative path of the .py file
        ```
        python /path/to/orion-inventory.py --list
        ```
        
**Running the Inventory in Ansible**
1. set execute permissions on the .py file using the command 
        ```
        chmod +x + /path/to/orion-inventory.py
        ```
2. Invoke ansible cli using the -i flag 
        *ansible-inventory command*
        ```
        ansible-inventory -i /path/to/orion-inventory.py --list
        ```
        ```
        ansible-inventory -i /path/to/orion-inventory.py --graph
        ```
        ```
        ansible-inventory -i /path/to/orion-inventory.py --host "HOSTGOESHERE"
        ```
        *ansible adhoc command*
        
        ```
        ansible -m ping "HOSTGOESHERE" -i /path/to/orion-inventory.py
        ```
