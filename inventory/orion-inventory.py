#!/usr/bin/python

###############################
### Author: Andy Escolastico
### Date: 01/26/2021
###############################

import requests
import json
import argparse
import re
import warnings
import sys

try:
    from creds import orion_creds
except:
    pass

class OrionInventory(object):
    def __init__(self):
        # read command line arguments and determine what methods to invoke
        self.read_cli_args()
        if self.args.list:
            self.inventory = self.collect_inventory()
        elif self.args.host:
            self.inventory = self.empty_inventory()
        else:
            self.inventory = self.empty_inventory()
        # print result
        print(json.dumps(self.inventory))
    def read_cli_args(self):
        # parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        parser.add_argument('--server', action = 'store')
        parser.add_argument('--username', action = 'store')
        parser.add_argument('--password', action = 'store')
        self.args = parser.parse_args()
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}        
    @staticmethod
    def normalize_inventory(item):
        # ansible is deprecating leading non word characters in group names
        if re.match(r"^[\d\W]|[^\w]", item):
            # prepend _ to satisfy new requirement
            item = "_" + item 
        # subtitute any non alphanumerics found in entire string
        item = re.sub('[^A-Za-z0-9]+', '_', item)
        # capitalize for readability
        item = item.upper()
        return item
    def validate_credentials(self):
        # handle errors related user input 
        if self.args.server and self.args.username and self.args.password:
            self.server = self.args.server
            self.username = self.args.username
            self.password = self.args.password
        elif "creds.orion_creds" in sys.modules:
            if orion_creds.server and orion_creds.username and orion_creds.password:
                self.server = orion_creds.server
                self.username = orion_creds.username
                self.password = orion_creds.password
            else:
                sys.exit("[ERROR] No creds found. Please provide credentials either by passing the script arguments or by populating a 'creds/orion_creds.py' file")
        else:
            sys.exit("[ERROR] No creds found. Please provide credentials either by passing the script arguments or by populating a 'creds/orion_creds.py' file")
    def collect_inventory(self):
        # define connection variables
        self.validate_credentials()
        server = self.server
        username = self.username
        password = self.password
        url = "https://" + server + ":17778/SolarWinds/InformationService/v3/Json/Query"
        query = "SELECT n.IPAddress, p.CWID, p.CustomerName, n.NodeDescription FROM Orion.Nodes AS n JOIN Orion.NodesCustomProperties AS p on n.NodeID = p.NodeID WHERE n.Status!= 9"
        params = "query=" + query
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        # perform data request
        response = requests.get(url, params=params, verify=False, auth=(username, password))
        data = (response.json())["results"]
        # define root dictionary to be populated
        inv = {
            'all': {
                'hosts': [],
                'vars': {},
            },
            '_meta': {
                'hostvars': {}
            },
            'ungrouped': {
                'hosts': []
            }
        }
        # enumerate through data set
        for i in data:
            # define the datapoints
            ip = i["IPAddress"]
            cwmid = i["CWID"]
            customer = self.normalize_inventory(i["CustomerName"])
            ndesc = i["NodeDescription"]
            # determine platform string
            if "Cisco IOS" in ndesc:
                platform = "ios"
            elif "Cisco Adaptive Security Appliance" in ndesc:
                platform = "asa"
            elif "Cisco NX-OS" in ndesc:
                platform = "nxos"
            elif "Palo Alto Networks" in ndesc:
                platform = "panos"
            elif "Juniper" in ndesc:
                platform = "junos"
            elif "Forti" in ndesc:
                platform = "fortios"
            elif "Meraki" in ndesc:
                platform = "meraki"
            elif "Silverpeak" in ndesc:
                platform = "silverpeak"
            elif "SonicWALL" in ndesc:
                platform = "sonicwall"
            else:
                platform = "unknown"
            # add host + hostvars to group '_meta'
            inv['_meta']['hostvars'][ip] = {
                'ansible_network_os': platform
            }
            # add host to group 'ungrouped' if 'customer name' field is empty
            if customer is None:
                inv['ungrouped']['hosts'].append(ip)
            # create group 'customer name' and add host + groupvars if not exist
            elif customer not in inv:
                inv[customer] = {
                    'hosts': [ip],
                    'vars': {
                        'CWM_RECID': cwmid
                    }
                }
            # add host to group 'customer name' if exist
            else:
                inv[customer]['hosts'].append(ip)
        # return final inventory
        return inv
OrionInventory()
