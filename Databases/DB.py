from sqlalchemy import create_engine, insert, update
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean
from sqlalchemy.orm import Session, sessionmaker
from Telnet import Alarm


class AlarmDatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///sqlite4.db')
        self.create_alarm_table()
        # engine.connect()
        # sessionmaker(bind=engine)

    def create_alarm_table(self):
        metadata = MetaData()
        self.alarms = Table('alarms', metadata,
                            Column('id', Integer(), nullable=False),
                            Column('type', String(7), nullable=False),
                            Column('date_time', String(15), nullable=False),
                            Column('managed_object', String(30)),
                            Column('object_name', String(30)),
                            Column('slogan', String(30)),
                            Column('descr', String(60)),
                            Column('text', String(300), nullable=False),
                            Column('is_active', Boolean(), nullable=False)
                            )
        print(metadata.create_all(self.engine))

    def insert_new_alarms(self, alarm_object: list[Alarm]):
        req = insert(self.alarms).values(
            [
                {
                    'id': alarm.id,
                    'type': alarm.type,
                    'date_time': alarm.date_time,
                    'managed_object': alarm.managed_object,
                    'object_name': alarm.object_name,
                    'slogan': alarm.slogan,
                    'descr': alarm.descr,
                    'text': alarm.text,
                    'is_active': alarm.is_active
                } for alarm in alarm_object
            ]
        )
        conn = self.engine.connect()
        conn.execute(req)

    def update_ceased_alarms(self, alarms_id: list[int]):
        conn = self.engine.connect()
        t = conn.begin()
        for _id in alarms_id:
            upd = update(self.alarms).where(
                self.alarms.c.id == _id
            ).values({'is_active': False})
            conn.execute(upd)
        t.commit()
