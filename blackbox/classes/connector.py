# -*- coding: utf-8 -*-

import mysql.connector
import logging

class Connector():
    def __init__(self, user, password, host, db):
        self.user = user
        self.password = password
        self.host = host
        self.database = db
        
        self.cnn = self.connect_db()
        self.cursor = self.cnn.cursor()
        
    def connect_db(self):
        cnn = None
        
        try:
            cnn = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
        except mysql.connector.Error as e:
            logging.info('connect fails!{}'.format(e))
        finally:
            return cnn
    
    def query(self, sql_str):
        try:
            self.cursor.execute(sql_str)
        except:
            logging.info("query data error: %s " % sql_str)
            self.close()
            
    def close(self):
        self.cursor.close()
        self.cnn.close()