import sqlite3
import psycopg2
con = sqlite3.connect('db.sqlite3')

database = 'df1r3bqgqk472g'
user = 'soforgvpxdcqva'
host = 'ec2-35-174-122-153.compute-1.amazonaws.com'
port = '5432'
password = '4cad74d3ad8cc1b1b65ab6ce1f921a849739b555117892786a1c98d3fa829d62'
conn=psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
cur2=conn.cursor()
cur = con.cursor()
old=cur.execute('''SELECT * FROM  "user"''')

for row in old:

    #cur2.execute('INSERT INTO "user" VALUES '+str(row))
    print(row)
con.commit()
con.close()
conn.commit()
conn.close()
