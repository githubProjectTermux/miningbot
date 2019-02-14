## SQL Tutorials https://www.w3schools.com/sql/sql_create_db.asp ##

import pyodbc

Server_IP = "192.168.1.149"
Database = "RigDetails"
Username = "sa"
Password = "p@ssw0rd"

con = pyodbc.connect('DRIVER={SQL Server};SERVER={0};DATABASE={1};UID={2};PWD={3}'.format(Server_IP, Database, Username, Password))

cursor = con.cursor()

cursor.execute("""
	CREATE TABLE RigDetails
	(
	RD_id int,

	)
	""")

cursor.close()
cont.close()
