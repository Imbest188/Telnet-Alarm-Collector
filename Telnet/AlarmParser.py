import re
from datetime import datetime as dt
import json





class AlarmParser:

    @staticmethod
    def parse_node_output(output_data) -> list:
        alarms = []
        head = 'allip;\nALARM LIST\n\n'
        for block in output_data \
                .replace('\r', '') \
                .replace(head, '') \
                .replace('ALARM SLOGAN', 'ALARM_SLOGAN') \
                .split('\n\n\n'):
            if re.findall(r'[A|O][1-3]', block):
                alarms.append(Alarm(block.strip()))
        return alarms
