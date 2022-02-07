import telnetlib
from threading import Thread
import time
import socket


class EricssonTelnet:
    __ip = ''
    __login = ''
    __password = ''
    __telnet = None
    __is_busy = True
    __alarms = []
    __is_alive = False

    def __init__(self, ip, login, password):
        self.__ip = ip
        self.__login = login
        self.__password = password
        self.__connect()
        self.__run_listening()

    def get_auth_data(self) -> dict:
        return {'host': self.__ip, 'login': self.__login, 'pwd': self.__password}

    def set_auth_data(self, ip, login, pwd):
        self.__ip = ip
        self.__login = login
        self.__password = pwd
        self.__connect()

    def is_alive(self):
        return self.__is_alive

    def __connect(self):
        print(f'Подключение к {self.__ip}')
        try:
            self.__telnet = telnetlib.Telnet(self.__ip)
        except ConnectionError:
            self.__telnet = None
            print("Не удалось подключиться к " + self.__ip)
            self.__is_alive = False
            return False
        self.__auth()
        time.sleep(1)
        self.__is_alive = True
        self.__listen_mode()
        print("\nСоединение с " + self.__ip + ' установлено')
        return True

    def __heartbeat(self):
        self.__is_busy = True
        self.__telnet.write(b'\r\n')
        self.__telnet.write(b'\x04')
        self.__is_busy = False

    def __parse(self, alarm_text):
        for alarm in alarm_text.split('END'):
            if len(self.__alarms) > 1000:
                self.__alarms.pop(0)
            self.__alarms.append(alarm.strip())

    @staticmethod
    def __clean_special_symbols(text):
        return text.replace('\x04', '').replace('<', '').replace('\x03', '').strip()

    def get_alarms(self):
        result = []
        for alarm in self.__alarms:
            if len(alarm) and alarm not in ['\x04', '<']:
                alarm_text = self.__clean_special_symbols(alarm)
                result.append(alarm_text)
        self.__alarms.clear()
        return result

    def __listening(self):
        self.__telnet.read_very_eager()
        seconds_counter = 0
        while True:
            time.sleep(1)
            if self.__is_busy:
                seconds_counter = 0
            else:
                try:
                    channel_output = self.__telnet.read_very_eager().decode('ascii')
                    seconds_counter += 1
                    if seconds_counter > 100 or 'Timeout' in channel_output:
                        seconds_counter = 0
                        self.__heartbeat()
                    self.__parse(channel_output)
                except ConnectionError:
                    self.__connect()

    def __run_listening(self):
        Thread(target=self.__listening, daemon=True).start()

    def __listen_mode(self):
        self.__telnet.write(b'\x04')
        self.__is_busy = False

    def __check_connection(self):
        try:
            self.__telnet.write(b'\r\n')
            time.sleep(0.2)
            check_state = self.__telnet.read_very_eager().decode('ascii').lower()
            if 'timeout' in check_state or 'login' in check_state:
                self.__connect()
                self.__telnet.write(b'\r\n')
        except ConnectionError:
            print(f'Переподключение к хосту {self.__ip}')
            self.__connect()
            self.__telnet.write(b'\r\n')

    def get(self, message) -> str:
        while self.__is_busy:
            time.sleep(0.2)
        self.__is_busy = True
        self.__check_connection()
        self.__telnet.write(message.encode('ascii') + b'\r\n')
        result = ''
        for count in range(30):
            result += self.__telnet.read_very_eager().decode('ascii')
            time.sleep(0.2)
            if 'END' in result or 'CELL NOT DEFINED' in result or 'EXTERNAL' in result:
                break

        self.__listen_mode()
        return result

    def send(self, message, accepting=True):
        while self.__is_busy:
            time.sleep(0.2)
        self.__is_busy = True
        self.__check_connection()
        self.__telnet.write(message.encode('ascii') + b'\r\n')
        time.sleep(0.5)
        if accepting:
            self.__telnet.write(b';\r\n\r\n')
        result = self.__telnet.read_very_eager().decode('ascii').lower()
        self.__listen_mode()
        if 'ordered' in result or 'executed' in result or 'preop' in result:
            return True
        return False

    def __auth(self):
        time.sleep(1)
        for i in range(6):
            time.sleep(1)
            answer = self.__telnet.read_very_eager()
            if b'login' in answer:
                self.__telnet.write(self.__login.encode('ascii') + b'\r\n')
            elif b'assword' in answer:
                self.__telnet.write(self.__password.encode('ascii') + b'\r\n')
            elif b'terminal' in answer:
                self.__telnet.write(b'xterm\r\n')
            elif b'Domain' in answer:
                self.__telnet.write(b'\r\n')
                time.sleep(1)
            elif b'WO' in answer or b'Login ok' in answer:
                break

        self.__telnet.write(b'\r\n')
        self.__telnet.write(b'mml -a\r\n')

    def __del__(self):
        self.__telnet.write(b'exit;')
        self.__telnet.get_socket().shutdown(socket.SHUT_WR)
        self.__telnet.read_all()
        self.__telnet.close()
        self.__telnet = None
