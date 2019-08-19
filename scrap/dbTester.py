"""
Playground to test out sqlite3 database logic.
"""
import sqlite3


conn = sqlite3.connect("scrap/markets.db")
cur = conn.cursor()

# Create table
# cur.execute('''CREATE TABLE stocks
#              (ID INTEGER PRIMARY KEY, date text, trans text, symbol text, qty real, price real)''')

# Insert a row of data
# cur.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")


# # Larger example that inserts many records at a time
# purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
#              ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
#              ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
#             ]
# cur.executemany('INSERT INTO stocks(date, trans, symbol, qty, price) VALUES (?,?,?,?,?)', purchases)

# # Save (commit) the changes
# conn.commit()

# # We can also close the connection if we are done with it.
# # Just be sure any changes have been committed or they will be lost.
# conn.close()


# SELECT QUERY

conn = sqlite3.connect("scrap/markets.db")
cur = conn.cursor()

# Test update query rowcount 
stonk_record = ('dummy_date', 15) 

sql_statement = '''SELECT * FROM stocks WHERE ID=100'''

res = cur.execute(sql_statement).fetchone()


print("res (value if there is no such record) =\n", res)
# print("rowcount (this is the default value when nothing done) = \n", cur.rowcount)

# print("type(res[0]) = ", type(res[0]))
conn.close()

