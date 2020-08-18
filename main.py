from utawaku import archive_audio
import threading
import time
stop_threads = False
#Currently tracking: Polka, Suisei, PPT, Rushia
channel_ids = ['UCK9V2B22uJYu3N7eR_BT9QA','UC5CwaMl1eIgY8h02uZw7u8A', 'UCZlDXzGoo7d44bwdNObFacg', 'UCl_gCybOJRIgOXw6Qb4qJzQ',]
threads = []
class youtubeThread(threading.Thread):
    def __init__(self, threadID, channel):
        threading.Thread.__init__(self)
        self._threadID = threadID
        self._channel = channel
    
    def run(self):
        while True:
            print("Starting for channel " + self._channel)
            archive_audio(self._channel)
            global stop_threads
            if stop_threads:
                break

def create_threads():

    while True:
        for i in channel_ids:
            thread = youtubeThread(1, i)
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        stop_threads = True
        for t in threads:
            print(t)
            t.join()
            print(threads)

def main():
    create_threads()

if __name__ == "__main__":
    main()