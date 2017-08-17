import multiprocessing
from threading import Thread

class ThreadTest:
    @staticmethod
    def multiply(self, a, b):
        return a * b

    def runthread(self):
        thread1 = Thread(target = self.multiply, args = (self, 2, 3))
        thread1.daemon = True
        thread1.start()
        print(str(thread1.run()))
        thread1.join()

ThreadTest().runthread()