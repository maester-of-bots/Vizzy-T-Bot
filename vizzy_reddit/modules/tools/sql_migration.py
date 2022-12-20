from sql import *
from modules.cloud_sql import *


processed = get_all()

cloud = db()

conn = cloud.get_db()
cur = conn.cursor()

for id in processed:
    cur.execute(f"INSERT INTO reddit_bots (obj_id, bot) VALUES (%s, %s)", (id, 'vizzy_t_bot'))
    conn.commit()


cur.close()
conn.close()