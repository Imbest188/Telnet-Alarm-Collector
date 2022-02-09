from Telnet.EricssonTelnet import EricssonTelnet
from Telnet.EricssonNode import EricssonBsc
from Telnet.AlarmParser import AlarmParser
from Telnet.AlarmCollector import AlarmCollector

from Databases import DB
import time

def print_alarm(alarm):
    print(
        f'0={alarm.id} ACTIVE={alarm.is_active} 1={alarm.slogan} 2={alarm.descr} 3={alarm.date_time} '
        f'4={alarm.managed_object} 5={alarm.type} 6={alarm.object_name}'
    )

if __name__ == '__main__':

    #db = DB.AlarmDatabase()

    #telnet = EricssonBsc('10.140.3.7', 'ts_user', 'apg43l2@')
    #for item in AlarmParser.parse_node_output(telnet.get('allip;')):
    #    print(item)
    #print('###'.join(AlarmParser.parse_allip(telnet.get('allip;'))))



    '''
    t = EricssonBsc('172.25.157.99', 'administrator', 'Administrator1@')
    inst_alarms = t.read_alarms()
    db.insert_new_alarms(inst_alarms)
    for alarm in inst_alarms:
        print_alarm(alarm)

    while True:
        time.sleep(5)#input()
        alarms = t.get_new_alarms()
        [x.id for x in alarms]
        for alarm in alarms:
            print_alarm(alarm)
        if len(alarms):
            new_alarms = [x for x in alarms if x.is_active]
            ceased = [x.id for x in alarms if not x.is_active]
            if len(new_alarms):
                db.insert_new_alarms(new_alarms)
            if len(ceased):
                db.update_ceased_alarms(ceased)
    '''
    a = AlarmCollector()
    #a.add_node('10.140.3.7', 'ts_user', 'apg43l2@', 'BSC04', 'bsc')
    #a.add_node('172.25.157.99', 'administrator', 'Administrator1@', 'BSC03', 'bsc')
    #a.add_node('10.140.27.68', 'ts_user', 'apg43l1@', 'BSC05', 'bsc')

    '''while True:
        time.sleep(10)
        changes = a.get_changes()
        print(changes)
        for node in changes.keys():
            new_alarms = [x for x in changes[node] if x.is_active]
            ceased_alarms = [x for x in changes[node] if not x.is_active]
            db.insert_new_alarms(new_alarms)
            db.update_ceased_alarms(ceased_alarms)
        print('*' * 10)'''



