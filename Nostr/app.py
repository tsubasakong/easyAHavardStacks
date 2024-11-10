import os,threading,signal
import time
import traceback
from dotenv import load_dotenv
from nostr_bot import NostrBot
from sql_actor import DBManager
from bot_factory import ChatBotFactory
# from BotAPI.api import BotAPI
load_dotenv()

Bot_npub = os.getenv('BOT_NPUB')
Bot_nsec = os.getenv('BOT_NSEC')
Bot_name = os.getenv('BOT_NAME')
chatbase_api_key = os.getenv('CHATBASE_API_KEY')
openai_api_key = os.getenv("OPENAI_API_KEY")
BotId = os.getenv('BOT_ID')
DB_NAME=os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
Password = os.getenv('DB_PASSWORD')
test_room_id = os.getenv('TEST_ROOM_ID')


class Partial(object):
    def __init__(self, func, *args, **keywords):
        self.func = func
        self.args = args
        self.keywords = keywords

    def __call__(self, *args, **keywords):
        args = self.args + args
        keywords = dict(self.keywords, **keywords)
        return self.func(*args, **keywords)
    
def signal_handler(signum,frame,event):
    print("Received signal:", signum)
    time.sleep(5)
    exit()


if __name__ == '__main__':
    stop_event = threading.Event()
    try:
        # Setup
        db_info = {
            "host": "db",
            "port": "5432",
            "database": DB_NAME,
            "user": DB_USER,
            "password": Password
        }
        db_actor = DBManager(db_info)
        if db_actor.conn is None:
            raise Exception("connect DB failed")
        db_actor.create_tables()
        
        # use chatbase API
        NewBot = NostrBot("relays.test",Bot_name,Bot_npub,Bot_nsec,BotId,chatbase_api_key,db_actor,test_room_id)
        
        ret = NewBot.connect_relays()
        if ret is not None:
            raise Exception("connect relays failed")
        NewBot.StartThread(event=stop_event)
        handler_with_args = Partial(signal_handler, event=stop_event)
        signal.signal(signal.SIGINT, handler_with_args)
        signal.pause()
        stop_event.set()
        NewBot.fetching_thread.join()
        NewBot.read_dm_thread.join()
        NewBot.read_channelchat_thread.join()
    except Exception as e:
        message = '[ERR]:Bot Stop: ' + str(e)
        print(message)
        error_traceback = traceback.format_exc()  # Get error traceback
        print("Error traceback: ", error_traceback)
        stop_event.set()
    
    print(f"BYE Karma!")