from nostr.relay_manager import RelayManager
from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.event import EncryptedDirectMessage
from nostr.key import PrivateKey,PublicKey
import os,datetime,time,json,ssl,functools,threading
from bot_factory import ChatBotFactory
# from BotAPI import ChatBaseAPI
import numpy as np

from sql_actor import DBManager

class NostrBot:
    def __init__(self, relays: str,name: str, pub: str,sec: str, botid:str, api_key: str,db_actor:DBManager, test_room_id:str) -> None:
        self.name=name
        self.relay_file=relays
        self.relay_manager=RelayManager()
        self.npub= pub
        self.botid = botid
        self.api_key = api_key
        self.private_key=PrivateKey.from_nsec(sec)
        self.db_actor = db_actor
        self.test_room_id = test_room_id
 
        print("[INFO]bot npub:", self.npub)
        print(f"[INFO]Hello, I am bot named {self.name},launch time is {datetime.datetime.now()}")
        factory = ChatBotFactory('GPT', chatbot_name=self.name, chatbot_id=self.botid, api_key=self.api_key)
        self.bot = factory.get_bot()
        # self.push_room_chat("Hello, I am bot named "+self.name, self.test_room_id)
        # self.bot = ChatBaseAPI(chatbot_name=self.name, chatbot_id=self.botid,api_key=self.api_key)
    
  
    def StartThread(self,event:threading.Event):
        try:
            self.fetching_thread = threading.Thread(target=self.fetch_msg_and_save,args=(event,))
            self.fetching_thread.start()
            self.read_dm_thread = threading.Thread(target=self.read_dm_answer,args=(event,))
            self.read_dm_thread.start()
            # self.read_channelchat_thread = threading.Thread(target=self.read_channelchat_answer,args=(event,))
            # self.read_channelchat_thread.start()
            event.wait()
        except Exception as e:
            message = '[ERR]:Bot threads stop: ' + str(e)
            print(message)
            event.set()

    def fetch_msg_and_save(self,stop_event:threading.Event,round_sec=3):
        print(f"[INFO]:Begin read msg from relays")
        
        # Add dm filter
        since_stamp = self.db_actor.get_dm_LatestTime()+5
        print(f"[INFO]:Start subcription from {since_stamp}")
        pubkey = PublicKey.from_npub(self.npub)
        dm_filter = Filter(
            pubkey_refs=[pubkey.hex()],
            kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
            since = since_stamp
            )
        filters = Filters([dm_filter])
        subscription_id = self.npub
        request = [ClientMessageType.REQUEST,subscription_id]
        request.extend(filters.to_json_array())
        self.relay_manager.add_subscription_on_all_relays(subscription_id, filters)
        while not stop_event.is_set():
            while self.relay_manager.message_pool.has_events():
                try:
                    event_msg = self.relay_manager.message_pool.get_event()
                    if event_msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                        print(f"[INFO]:recv events {datetime.datetime.now()}")
                        print(f"[INFO]:note id:{event_msg.event.note_id}")
                        print(f"[INFO]:note kind:{event_msg.event.kind}")
                        send_pub=PublicKey(bytes.fromhex(event_msg.event.public_key)).bech32()
                        print(f"[INFO]:sender key:{send_pub}")
                        print(f"[INFO]:tags:{event_msg.event.tags}")
                        print(f"[INFO]:content:{event_msg.event.content}")
                        if event_msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                            msg = self.private_key.decrypt_message(event_msg.event.content,event_msg.event.public_key)
                            print(f"[INFO]:decrypt content:{msg}")
                        if self.db_actor.add_dm(send_pub,event_msg.event.note_id,event_msg.event.created_at,msg) is False:
                            raise Exception("DB transaction error")
                    # if event_msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                        # print(f"[INFO]:recv events {datetime.datetime.now()}")
                except Exception as e:
                    print("[ERR]:something wrong happend! clean the context:",e)
                    stop_event.set()
                time.sleep(round_sec)
            time.sleep(round_sec)

        print("[INFO]close all connnections")
        self.relay_manager.close_all_relay_connections()

    def read_dm_answer(self,stop_event:threading.Event,round_sec=3):
        print(f"[INFO]:Begin read dm msg from DB")
        try:
            # check 
            while (not stop_event.is_set()) and (self.db_actor.check_dm_records(0) is not None):
                #POC: no context
                data = self.db_actor.read_dm()
                if data is not None:
                    print(f"[INFO]message dm to {self.bot.chatbot_name}")
                    received_msg = data[4]
                    print("[INFO]received_msg:",received_msg, "len:",len(received_msg))
                    # message=[
                    #         {"content": "", "role": "assistant"},
                    #         {"content": f"{data[4]}", "role": "user"}
                    #     ]
                    id = data[1]+"-dm"
                    print("[INFO]id:",id,"len:",len(id))
                    resp = self.bot.message_chatbot(id,received_msg)
                    self.dm(PublicKey.from_npub(data[1]).hex(),resp['text'])
                    self.db_actor.update_dm(data[0],resp['text'])
                    time.sleep(round_sec)
                time.sleep(round_sec)
        except Exception as e:
            message = '[ERR]:read_dm_answer logic stop: ' + str(e)
            print(message)
        
        print("[INFO]exit read_dm_answer")

    def read_channelchat_answer(self,stop_event:threading.Event,round_sec=3):
        print(f"[INFO]:Begin read channel msg from DB")
        try:
            
            # check 
            while (not stop_event.is_set()) and (self.db_actor.check_group_records(0) is not None):
                #POC: no context
                data = self.db_actor.read_groupchat() 
                print(f"[INFO]data:{data}")
                if data is not None:
                    print(f"message channelchat to {self.bot.chatbot_name}")
                    
                    # message=[
                    #         {"content": "", "role": "assistant"},
                    #         {"content": f"{data[5]}", "role": "user"}
                    #     ]
                    # id = data[1]+"-dm"
                    # resp = self.bot.message_chatbot(id,message)
                    # print(f"response content:{resp}")
            time.sleep(round_sec)

        except Exception as e:
            message = '[ERR]:read_channelchat_answer logic stop: ' + str(e)
            print(message)
        
        print("[INFO]exit read_channelchat_answer")

    def connect_relays(self):
        try:
            relays = np.loadtxt(self.relay_file, delimiter=';',dtype='str')
            if relays.ndim == 0:
                print(f"add relay:{relays}")
                self.relay_manager.add_relay(relays.item())
            else:
                print(f"start connecting to {len(relays)} relays at {datetime.datetime.now()}")
                for r in relays:
                    # print(f"add relay:{r}")
                    self.relay_manager.add_relay(r) 
                    
            self.push_room_chat("Hello, I am bot named "+self.name, self.test_room_id)
            return None
        except Exception as e:
            message = '[ERR]:connecting relay stop: ' + str(e)
            print(message)
            return e


    def push_note(self,message):
        event = Event(message)
        self.private_key.sign_event(event)
        self.relay_manager.publish_event(event)
        print("[INFO]publish notes:",message)

        time.sleep(5) # allow the messages to send

    def reply_note(self,original_note_author_pubkey,original_note_id,message):
        reply = Event(
        content=message,
        )

        # create 'e' tag reference to the note you're replying to
        reply.add_event_ref(original_note_id)

        # create 'p' tag reference to the pubkey you're replying to
        reply.add_pubkey_ref(original_note_author_pubkey)

        self.private_key.sign_event(reply)
        self.relay_manager.publish_event(reply)

    def dm(self,recipient_pubkey,message):
        dm = EncryptedDirectMessage(
        recipient_pubkey=recipient_pubkey,
        cleartext_content=message
        )
        self.private_key.sign_event(dm)
        self.relay_manager.publish_event(dm)

    # NIP-28, kind 42, https://github.com/nostr-protocol/nips/blob/master/28.md
    def push_room_chat(self, message, room_id):
        event = Event(kind=EventKind.CHANNEL_MSG, content=message,)
        event.add_event_ref(room_id, 'wss://relay01.karma.svaha-chain.online','root')
        # event.add_ws_ref('wss://relay01.karma.svaha-chain.online')
        # event.add_marker_ref("root")
        self.private_key.sign_event(event)
        self.relay_manager.publish_event(event)
        time.sleep(5)  # allow the messages to send

    def close_connections(self):
        self.relay_manager.close_all_relay_connections()


