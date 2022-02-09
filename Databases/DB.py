from sqlalchemy import create_engine, insert, update, delete, select, exc
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean
from Telnet import Alarm


class AlarmDatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///sqlite4.db')
        self.create_alarm_table()
        self.clear_alarm_table()

    def clear_alarm_table(self):
        conn = self.engine.connect()
        conn.execute(delete(self.alarms))

    def create_alarm_table(self):
        metadata = MetaData()
        self.alarms = Table('alarms', metadata,
                            Column('id', Integer(), nullable=False),
                            Column('type', String(7), nullable=False),
                            Column('raising_time', String(15), nullable=False),
                            Column('ceasing_time', String(15), nullable=True),
                            Column('managed_object', String(30)),
                            Column('object_name', String(30)),
                            Column('slogan', String(30)),
                            Column('descr', String(60)),
                            Column('text', String(300), nullable=False),
                            Column('is_active', Boolean(), nullable=False),
                            Column('node_id', Integer())
                            )

        self.nodes = Table('nodes', metadata,
                           Column('id', Integer(), autoincrement=True, primary_key=True),
                           Column('name', String(20), nullable=False, unique=True),
                           Column('update_id', Integer(), default=0)
                           )
        metadata.create_all(self.engine)

    def insert_new_alarms(self, alarm_objects: list[Alarm]):
        if not len(alarm_objects):
            return
        query = insert(self.alarms).values(
            [
                {
                    'id': alarm.id,
                    'type': alarm.type,
                    'raising_time': alarm.raising_time,
                    'managed_object': alarm.managed_object,
                    'object_name': alarm.object_name,
                    'slogan': alarm.slogan,
                    'descr': alarm.descr,
                    'text': alarm.text,
                    'is_active': alarm.is_active,
                    'node_id': alarm.node_id
                } for alarm in alarm_objects
            ]
        )
        conn = self.engine.connect()
        conn.execute(query)

    def update_ceased_alarms(self, alarm_objects: list[Alarm]):
        if not len(alarm_objects):
            return
        conn = self.engine.connect()
        transaction = conn.begin()
        for alarm in alarm_objects:
            upd = update(self.alarms).where(
                self.alarms.c.id == alarm.id
            ).values({'is_active': False, 'ceasing_time': alarm.ceasing_time})
            conn.execute(upd)
        transaction.commit()

    def increase_update_id(self, controller_id):
        conn = self.engine.connect()
        upd = update(self.nodes).where(
            self.nodes.c.id == controller_id
        ).values(
            {'update_id': self.nodes.c.update_id + 1 if self.nodes.c.update_id < 9 else 0}
        )
        conn.execute(upd)

    def add_node(self, node_name):
        conn = self.engine.connect()
        query = insert(self.nodes).values(
            {
                'name': node_name,
                'update_id': 0
            }
        )
        try:
            conn.execute(query)
        except exc.IntegrityError:
            pass

    def get_node_id(self, name) -> int:
        conn = self.engine.connect()
        query = select(self.nodes.c.id).where(
            self.nodes.c.name == name
        )
        result = conn.execute(query).fetchone()
        return result[0]
