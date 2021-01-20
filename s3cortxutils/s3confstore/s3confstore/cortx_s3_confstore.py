#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

#!/usr/bin/python3.6

import argparse
from cortx.utils.conf_store import Conf
from urllib.parse import urlparse
import os.path
import json
import sys
import inspect
from cortx.utils.kv_store import kv_store_collection

class S3CortxConfStore:

  def __init__(self, config: str = None, index: str = "default_cortx_s3_confstore_index"):
    """Instantiate confstore"""
    self.config_file = config
    self.default_index = index

    if config is not None:
      self.validate_configfile(config)
      self.load_config(self.default_index, self.config_file)

  @staticmethod
  def load_config(index: str, config: str):
    """Load Config into confstore"""
    Conf.load(index, config)

  def get_config(self, key: str):
    """Get the key's config from confstore"""
    return Conf.get(self.default_index, key)

  def set_config(self, key: str, value: str, save: bool = False):
    """Set the key's value in confstore"""
    Conf.set(self.default_index, key, value)
    if save == True:
      """Update the index backend"""
      Conf.save(self.default_index)

  @staticmethod
  def validate_configfile(configfile: str):
    if os.path.isfile(urlparse(configfile).path) != True:
      print("config file: {} does not exist".format(configfile))
      sys.exit(1)
    else:
      store_type = urlparse(configfile).scheme
      is_valid_type = False
      valid_types = ''
      storage = inspect.getmembers(kv_store_collection, inspect.isclass)
      for name, cls in storage:
        if hasattr(cls, 'name') and name != "KvStore":
          valid_types += cls.name + ' '
          if store_type == cls.name:
            is_valid_type = True
            break

      if is_valid_type == False:
        print("Invalid storage type {} in config file: {}, accepted types are {}".format(store_type, configfile, valid_types))
        sys.exit(1)

      if store_type == 'json':
        try:
          with open(urlparse(configfile).path) as f:
            json.load(f)
        except ValueError as e:
          print("config file: {} must use valid JSON format: {}".format(urlparse(configfile).path, e))
          sys.exit(1)
      """TODO: Implement rest of the type's content validators here"""

  def get_nodecount(self):
    nodes_count = None
    key_to_read_from_conf = 'cluster>server_nodes'

    dict_servernodes = self.get_config(key_to_read_from_conf)
    if dict_servernodes:
      nodes_count = len (dict_servernodes)
    else:
      print("Failed to read key: {} from confstore".format(key_to_read_from_conf))

    return nodes_count

  def get_privateip(self, machine_id: str):
    privateip = ""
    key_to_read_from_conf = 'cluster>server_nodes'

    dict_servernodes = self.get_config(key_to_read_from_conf)

    # find the 'machine_id' in the keys of dict_servernodes
    server_node = ""
    if machine_id in dict_servernodes.keys():
      server_node = dict_servernodes[machine_id]
      privateip = self.get_config("cluster>{}>network>data>private_ip".format(server_node))
    else:
      print("Failed to read private ip of node: {}".format(server_node))

    return privateip

  def get_nodenames_list(self):
    nodes_list = []
    key_to_read_from_conf = 'cluster>server_nodes'

    machineid_server_dict = self.get_config(key_to_read_from_conf)
    if machineid_server_dict:
      srvrnodes_list = machineid_server_dict.values()
      for server in srvrnodes_list:
        host = self.get_config("cluster>{}>hostname".format(server))
        if host is not None:
          nodes_list.append(host)
        else:
          print("Failed to get hostname for key cluster>{}>hostname".format(server))
          sys.exit(1)
    return nodes_list

  def run(self):
    parser = argparse.ArgumentParser(description='cortx-py-utils::ConfStore wrapper')

    parser.add_argument("config",
                        help='config file url, check cortx-py-utils::confstore for supported formats.',
                        type=str)

    subparsers = parser.add_subparsers(dest='command', title='comamnds')

    getkey = subparsers.add_parser('getkey', help='get value of given key from confstore')
    setkey = subparsers.add_parser('setkey', help='set given value to given key in confstore')
    getnodecount = subparsers.add_parser('getnodecount', help='get count of nodes in the cluster')
    getnodenames = subparsers.add_parser('getnodenames', help='get FQDN of nodes in the cluster')
    getprivateip = subparsers.add_parser('getprivateip', help='get privateip of the host of given machine-id')

    getkey.add_argument('--key', help='Fetch value of the given key', type=str, required=True)

    setkey.add_argument('--key', help='set new value to given key', type=str)
    setkey.add_argument('--value', help='new value to be set to given key', type=str)

    getprivateip.add_argument('--machineid', help='machine-id of the host, whose private ip to be read', type=str, required=True)

    args = parser.parse_args()

    s3conf_store = S3CortxConfStore(args.config)

    if args.command == 'getkey':
      self.load_config(self.default_index)
      keyvalue = s3conf_store.get_config(args.key)
      if keyvalue:
        print("{}".format(keyvalue))
      else:
        sys.exit("Failed to get key:{}'s value".format(args.key))

    elif args.command == 'setkey':
      s3conf_store.set_config(args.key, args.value, True)

    elif args.command == 'getnodecount':
      nodes_count = s3conf_store.get_nodecount()
      if nodes_count:
        print("{}".format(nodes_count))
      else:
        sys.exit("Failed to get nodes count from confstore")

    elif args.command == 'getnodenames':
      nodes_list = s3conf_store.get_nodenames_list()
      if nodes_list:
        print("{}".format(nodes_list))
      else:
        sys.exit("Failed to get nodes list from confstore")

    elif args.command == 'getprivateip':
      private_ip = s3conf_store.get_privateip(args.machineid)
      if private_ip:
        print("{}".format(private_ip))
      else:
        sys.exit("Failed to read private ip from confstore of machineid: {}".format(args.machineid))

    else:
      sys.exit("Invalid command option passed, see help.")