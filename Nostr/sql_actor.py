import psycopg2

class DBManager:
    def __init__(self, db_info):
        """ initialize a database manager instance """
        # print(db_info)
        self.conn = self.create_connection(db_info)

    def create_connection(self, db_info):
        """ create a database connection """
        conn = None
        try:
            conn = psycopg2.connect(**db_info)
        except (Exception, psycopg2.Error) as e:
            print(e)
            return None

        print("[INFO]DB Connected")
        return conn
    
    def create_tables(self):
        c = self.conn.cursor()
        try:
            
            """ Create tables """
            c.execute('''CREATE TABLE IF NOT EXISTS dmchat 
                                (id SERIAL PRIMARY KEY, userid TEXT, noteid TEXT, timestamp INTEGER, notes TEXT, answer TEXT DEFAULT '');''')
            c.execute('''CREATE INDEX IF NOT EXISTS index_userid ON dmchat(userid);''')

            c.execute('''CREATE TABLE IF NOT EXISTS groupchat 
                                (id SERIAL PRIMARY KEY, channelid TEXT, userid TEXT, noteid TEXT, timestamp INTEGER, notes TEXT, answer TEXT DEFAULT '');''')
            c.execute('''CREATE INDEX IF NOT EXISTS index_channelid ON groupchat(channelid);''')

            c.execute('''CREATE TABLE IF NOT EXISTS note_dm_record 
                                (id SERIAL PRIMARY KEY, num INTEGER DEFAULT 0, read_index INTEGER DEFAULT 0);''')

            # insert a new record
            c.execute("INSERT INTO note_dm_record (id, num, read_index) VALUES (0, 0, 0) ON CONFLICT (id) DO NOTHING")


            c.execute('''CREATE TABLE IF NOT EXISTS note_group_record 
                                (id SERIAL PRIMARY KEY, num INTEGER DEFAULT 0, read_index INTEGER DEFAULT 0);''')

            # insert a new record
            c.execute("INSERT INTO note_group_record (id, num, read_index) VALUES (0, 0, 0) ON CONFLICT (id) DO NOTHING")
            self.conn.commit()
        except (Exception, psycopg2.Error) as e:
            print(e)

    def add_dm(self, userid, noteid, timestamp, notes):
        """ add a dm chat """
        c = self.conn.cursor()
        try:
            # check if the record exists
            c.execute("SELECT * FROM dmchat WHERE userid = %s AND noteid = %s", (userid, noteid,))
            data = c.fetchone()
            if data is None:
                # insert a new record
                c.execute("INSERT INTO dmchat (userid, noteid, timestamp, notes) VALUES (%s, %s, %s, %s)", (userid, noteid, timestamp, notes,))
                self.conn.commit()
                # update note_dm_record
                c.execute("UPDATE note_dm_record SET num = num + 1 WHERE id = 0")
                self.conn.commit()
                print(f"[INFO]Add dm {noteid} in dmchat")
        except (Exception, psycopg2.Error) as e:
            print(e)
            return False
        return True

    def add_groupchat(self, channelid, userid, noteid, timestamp, notes):
        """ add a group chat """
        c = self.conn.cursor()
        try:
            # check if the record exists
            c.execute("SELECT * FROM groupchat WHERE channelid = %s AND noteid = %s", (channelid, noteid,))
            data = c.fetchone()
            if data is None:
                # insert a new record
                c.execute("INSERT INTO groupchat (channelid, userid, noteid, timestamp, notes) VALUES (%s, %s, %s, %s, %s)", (channelid, userid, noteid, timestamp, notes,))
                self.conn.commit()
                # update note_group_record
                c.execute("UPDATE note_group_record SET num = num + 1 WHERE id = 0")
                self.conn.commit()
                print(f"[INFO]Add msg {noteid} in {channelid} groupchat")
        except (Exception, psycopg2.Error) as e:
            print(e)

    def get_dm_LatestTime(self):
        """ get the since timestamp """
        c = self.conn.cursor()
        
        c.execute("SELECT timestamp FROM dmchat ORDER BY id DESC LIMIT 1;")
        data = c.fetchone()

        if data is not None:
            return data[0]
        return 0
    
    def check_dm_records(self, id):
        """ check note_dm_record index and num """
        c = self.conn.cursor()

        c.execute("SELECT num, read_index FROM note_dm_record WHERE id = %s", (id,))
        data = c.fetchone()

        if data is not None:
            return data[0] - data[1], data[1]
        return None

    def check_group_records(self, id):
        """ check note_group_record index and num """
        c = self.conn.cursor()

        c.execute("SELECT num, read_index FROM note_group_record WHERE id = %s", (id,))
        data = c.fetchone()

        if data is not None:
            return data[0] - data[1], data[1]
        return None

    def read_dm(self):
        """ read an unknown direct message """
        c = self.conn.cursor()

        unread_num,index = self.check_dm_records(0)
        if unread_num is not None and unread_num > 0:
            c.execute("SELECT * FROM dmchat WHERE id > %s ORDER BY id ASC LIMIT 1", (index,))
            data = c.fetchone()
            if data is not None:
                return data
        return None

    def update_dm(self,id,msg):
        c = self.conn.cursor()
        c.execute("SELECT * FROM dmchat WHERE id = %s", (id,))
        data = c.fetchone()
        if data is not None:
            c.execute("UPDATE dmchat SET answer= %s WHERE id = %s", (msg,id,))
            self.conn.commit()
            # update note_dm_record
            c.execute("UPDATE note_dm_record SET read_index = %s WHERE id = 0", (id,))
            self.conn.commit()
            return True
        return False

    def read_groupchat(self):
        """ read an unknown group chat """
        c = self.conn.cursor()

        unread_num,index= self.check_group_records(0)
        if unread_num is not None and unread_num > 0:
            c.execute("SELECT * FROM groupchat WHERE id > %s ORDER BY id ASC LIMIT 1", (index,))
            data = c.fetchone()
            if data is not None:
                # update note_group_record
                c.execute("UPDATE note_group_record SET read_index = %s WHERE id = 0", (data[0],))
                self.conn.commit()
            return data
        return None
