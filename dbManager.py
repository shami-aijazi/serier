# Database manager for Series Slack app.
# This file creates the database and the tables of the application data model
import sqlite3


def create_db_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
 
    return None


def close_db(conn):
    """
    Commit changes and close DB connection
    """
    conn.commit()
    conn.close()

# First, create the database and establish the connection
db_conn = create_db_connection("serier.db")
curr = db_conn.cursor()

# Create the teams table
curr.execute('''CREATE TABLE IF NOT EXISTS teams
             (team_id VARCHAR, bot_token VARCHAR);''')

# Create the users table
curr.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id VARCHAR, team_id VARCHAR);''')

# Create the series table
curr.execute('''CREATE TABLE IF NOT EXISTS series
             (series_id INTEGER PRIMARY KEY, title VARCHAR, presenter VARCHAR,
             topic_selection VARCHAR, start_date DATE, end_date DATE, session_start TIME,
             frequency VARCHAR, num_sessions INTEGER, is_paused BOOLEAN);''')


# Create the sessions table
curr.execute('''CREATE TABLE IF NOT EXISTS sessions
             (session_id INTEGER PRIMARY KEY, series_id INTEGER, session_start TIME, presenter VARCHAR,
              topic DATE, is_skipped BOOLEAN, is_done BOOLEAN, is_modified BOOLEAN);''')

# Create the organizers table
curr.execute('''CREATE TABLE IF NOT EXISTS organizers
             (user_id VARCHAR, series_id INTEGER);''')



# Close the database in the end
close_db(db_conn)

