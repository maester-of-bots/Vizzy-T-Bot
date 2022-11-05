import sqlite3
from pathlib import Path

# Initial local file config
dbname = "VizzyTDB.db"
dbfolder = "db/"

# Create the local database folder if it doesn't exist
Path(dbfolder).mkdir(parents=True, exist_ok=True)


def sqlite_connect():
    """
    Create a local connection to the local database
    """

    global conn
    conn = sqlite3.connect(dbfolder + dbname, check_same_thread=False)
    conn.row_factory = lambda cursor, row: row[0]


def init_sqlite():
    """
    Connect to the local database and initialize the VizzyTDB.

    Swearbox table tracks specific users and how much they've contributed to the church roof
    comments table tracks all comment IDs that the bot has read / replied to
    """

    conn = sqlite3.connect(dbfolder + dbname)
    c = conn.cursor()
    c.execute('''CREATE TABLE comments (id text)''')
    c.execute('''CREATE TABLE depleted (id text)''')

def getComments():
    """Get all comment IDs from the comments table

    :return list: All comment IDs.
    """

    sqlite_connect()
    c = conn.cursor()
    c.execute("""SELECT id FROM comments""")
    result = c.fetchall()
    return result

def getCommentsdepleted():
    """Get all comment IDs from the comments table

    :return list: All comment IDs.
    """

    sqlite_connect()
    c = conn.cursor()
    c.execute("""SELECT id FROM depleted""")
    result = c.fetchall()
    return result


def writeComment(id):
    """Write a comment ID to the comments table

    :param str id:  The comment ID to record
    """

    sqlite_connect()
    c = conn.cursor()
    q = [(id)]
    c.execute('''INSERT INTO comments('id') VALUES(?)''', q)
    conn.commit()
    conn.close()


def writeDwarfComment(id):
    """Write a comment ID to the comments table

    :param str id:  The comment ID to record
    """

    sqlite_connect()
    c = conn.cursor()
    q = [(id)]
    c.execute('''INSERT INTO dwarf('id') VALUES(?)''', q)
    conn.commit()
    conn.close()


def getCommentsdwarf():
    """Get all comment IDs from the comments table

    :return list: All comment IDs.
    """

    sqlite_connect()
    c = conn.cursor()
    c.execute("""SELECT id FROM dwarf""")
    result = c.fetchall()
    return result

def writeCommentdepleted(id):
    """Write a comment ID to the comments table

    :param str id:  The comment ID to record
    """

    sqlite_connect()
    c = conn.cursor()
    q = [(id)]
    c.execute('''INSERT INTO depleted('id') VALUES(?)''', q)
    conn.commit()
    conn.close()


# Initialize the database if it's not already done
try:
    init_sqlite()
except:
    pass
