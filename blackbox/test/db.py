# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import mysql.connector

cnx = mysql.connector.connect(user='root', password='xxxx', host='127.0.0.1', database='test')
cursor = cnx.cursor()
query = ("select * from persons")
cursor.execute(query)
for (id, name) in cursor:
    print id
    print name
cursor.close()
cnx.close()
