import time
import threading
import os
import signal

class FiveSec(threading.Thread):
    def run(self, *args):
        while 1:
            time.sleep(.5)
            print('==============')
            # if time.time() >= self.my_timer:
            #     break
        # os.kill(os.getpid(), signal.SIGINT)


def main():
    try:
        t = FiveSec()
        t.daemon = True
        t.start()
        while 1:
            x = input()
    except KeyboardInterrupt:
        print("\nDone!")

if __name__ == '__main__':
    main()