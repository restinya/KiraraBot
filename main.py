from utawaku import archive_loop
import threading
import time
from discord_bot import launch_kirara

#Currently tracking: Polka, Suisei, PPT, Rushia
stop_threads = False
channel_ids = ['UCK9V2B22uJYu3N7eR_BT9QA','UC5CwaMl1eIgY8h02uZw7u8A', 'UCZlDXzGoo7d44bwdNObFacg', 'UCl_gCybOJRIgOXw6Qb4qJzQ',]
threads = []
class YoutubeThread(threading.Thread):
    def __init__(self, threadID, channel):
        threading.Thread.__init__(self)
        self._threadID = threadID
        self._channel = channel
    
    def run(self):
        while True:
            print("Starting for channel " + self._channel)
            archive_loop(self._channel)
            global stop_threads
            if stop_threads:
                break

class DiscordThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self._threadID = threadID

    def run(self):
        launch_kirara()

def create_threads():
    for i in channel_ids:
        thread = YoutubeThread(1, i)
        thread.start()
        threads.append(thread)
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        stop_threads = True
        for t in threads:
            print(t)
            t.join()
            print(threads)

if __name__ == "__main__":
    create_threads()