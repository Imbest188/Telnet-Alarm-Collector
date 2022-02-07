from . import EricssonTelnet
from . import EricssonNode
from . import AlarmParser

import json


class AlarmCollector:
    def __init__(self):
        self.__nodes = dict()
        self.__init_connections()

    def get_nodes(self) -> list:
        return list(self.__nodes.keys())

    def get_active_alarms(self, node_name) -> list:
        if node_name in self.__nodes.keys():
            pass
            #################self.__nodes[key].

    # may be async
    def add_node(self, host, login, password, name, node_type, override=True):
        node = EricssonNode.EricssonBsc(host, login, password) if node_type == 'bsc' \
            else EricssonTelnet.EricssonTelnet(host, login, password)
        if node.is_alive():
            self.__nodes[name] = node
            if override:
                self.__save_connections()
            return True
        return False

    def __init_connections(self):
        with open('nodes.ini', 'r+') as nodes:
            data = json.load(nodes)
            for node in data.keys():
                node_data = data[node]
                self.add_node(
                    host=node_data['host'],
                    login=node_data['login'],
                    password=node_data['pwd'],
                    name=node,
                    node_type=node_data['type'],
                    override=False
                )

    def __nodes_to_dict(self) -> dict:
        result = dict()
        for node in self.__nodes.keys():
            node_object = self.__nodes[node]
            node_type = 'bsc' if type(node_object) == EricssonNode.EricssonBsc else 'node'
            node_data = node_object.get_auth_data()
            node_data['type'] = node_type
            result[node] = node_data
        return result

    def __save_connections(self):
        with open('nodes.ini', 'w+') as nodes:
            json.dump(self.__nodes_to_dict(), nodes)
