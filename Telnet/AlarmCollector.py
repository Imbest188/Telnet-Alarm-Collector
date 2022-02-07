import time

from Telnet.EricssonNode import EricssonBsc, EricssonNode
from Databases.DB import AlarmDatabase
from threading import Thread

import json


class AlarmCollector:
    def __init__(self):
        self.__nodes = dict()
        self.__alarms = dict()
        self.__init_connections()
        self.__start_listening()
        self.__busy = False

    def get_nodes(self) -> list:
        return list(self.__nodes.keys())

    def __start_listening(self):
        Thread(target=self.__listening, daemon=True).start()

    def __listening(self):
        while True:
            time.sleep(5)
            if not self.__busy:
                for name in self.__nodes.keys():
                    new_alarms = self.__nodes[name].get_new_alarms()
                    self.__alarms[name] += new_alarms

    def __init_alarm_dict(self) -> dict:
        new_dict = dict()
        for name in self.__nodes.keys():
            new_dict[name] = []
        return new_dict

    def get_changes(self) -> dict[str: list]:
        self.__busy = True
        result = self.__alarms
        self.__alarms = self.__init_alarm_dict()
        self.__busy = False
        return result

    # may be async
    def add_node(self, host, login, password, name, node_type, override=True):
        node = EricssonBsc(host, login, password) if node_type == 'bsc' \
            else EricssonNode(host, login, password)
        if node.is_alive():
            self.__nodes[name] = node
            #self.__alarms[name] = []
            self.__alarms[name] = node.read_alarms()
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
            node_type = 'bsc' if type(node_object) == EricssonBsc else 'node'
            node_data = node_object.get_auth_data()
            node_data['type'] = node_type
            result[node] = node_data
        return result

    def __save_connections(self):
        with open('nodes.ini', 'w+') as nodes:
            json.dump(self.__nodes_to_dict(), nodes)
