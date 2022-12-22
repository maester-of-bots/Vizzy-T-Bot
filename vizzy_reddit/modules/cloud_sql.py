import psycopg2
from datetime import *

from dotenv import load_dotenv

import os

class db:
    def __init__(self):

        load_dotenv()

        self.server = os.getenv('cloud_db-URL')
        self.user = os.getenv("cloud_db-User")
        self.password = os.getenv("cloud_db-Key")
        self.port = os.getenv("cloud_db-Port")
        self.database = os.getenv('cloud_db-db')
        self.sslmode = os.getenv('cloud_db-ssl')

        print("sudo yum install python-devel postgresql-devel")
        print('sudo yum install python-psycopg2')
        try:
            self.init_sqlite()
        except:
            pass


    def usage_dump(self, user_id, username, command, prompt, cost, columns=None, table="openai_usage"):
        """
        Dump OpenAI usage data to the cloud database server
        """

        # Columns is always None
        if columns is None:
            columns = ['user_id', 'username', 'timestamp', 'command', 'prompt', 'cost']

        # Drop the data into the data list
        data = (user_id, username, str(datetime.now()), command, prompt, str(cost))



        conn = self.get_db()
        cur = conn.cursor()
        vals = ""
        for column in columns:
            vals += "%s, "

        columns = ", ".join(columns)

        vals = vals[0:-2]
        cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({vals})", data )
        conn.commit()
        # Close communication with the database
        cur.close()
        conn.close()


    def get_db(self):
        # connect to MySQL server
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.user,
            password=self.password,
            host=self.server,
            port=25060,
            sslmode='require')

        return conn

    # Create the SQL database
    def init_sqlite(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute(f"CREATE TABLE reddit_bots (obj_id varchar, bot varchar);")
        conn.commit()
        # Close communication with the database
        cur.close()
        conn.close()

    def write_obj(self, obj_id, bot):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO reddit_bots (obj_id, bot) VALUES (%s, %s)", (obj_id, bot))
        conn.commit()
        cur.close()
        conn.close()

    def check_db(self, obj_id, bot):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute(f"SELECT obj_id FROM reddit_bots WHERE obj_id LIKE '{obj_id}' AND bot LIKE '{bot}'")
        result = cur.fetchone()

        cur.close()
        conn.close()

        # We haven't made this comment yet
        if result is None:
            return False

        # We already commented.
        else:
            return True


