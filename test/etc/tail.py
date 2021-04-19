import os
import sys
import time
import threading

LOG_FILE_PATH = os.path.join(os.path.expanduser('~'),
                             'projects', 'Data', 'logs', 'MyTrading', 'MyTrading.log')

END = '\033[0m'
COLOR = {
    'CRITICAL' : '\033[91m',
    '   ERROR' : '\033[31m',
    ' WARNING' : '\033[95m',
    '    INFO' : '\033[93m',
    '   DEBUG' : '\033[37m',
}

def log_print(log):
    log_color = COLOR['   DEBUG']
    for key in COLOR.keys():
        if key in log:
            log_color = COLOR[key]
    print(log_color + log + END)

class ReadLog(threading.Thread):
    def run(self, *args):
        with open(LOG_FILE_PATH, 'r') as f:
            for line in f.readlines()[-10::]:
                log_print(line[:-1])

            f.seek(f.tell())
            while True:
                where = f.tell()
                line = f.readline()
                if not line:
                    time.sleep(.5)
                    f.seek(where)
                else:
                    log_print(line[:-1])

def main():
    log = ReadLog()
    log.daemon = True
    log.start()
    print('Type "exit" to exit the program!!')
    while True:
        x = input()
        if x == 'exit':
            sys.exit()


if __name__ == '__main__':
    main()