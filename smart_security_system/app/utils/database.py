import sqlite3
from datetime import datetime

class SecurityDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('security_logs.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         event_type TEXT NOT NULL,
         timestamp DATETIME NOT NULL,
         person_detected BOOLEAN,
         authorized BOOLEAN)
        ''')
        self.conn.commit()
        
    def log_event(self, event_type, person_detected=False, authorized=False):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO security_events (event_type, timestamp, person_detected, authorized)
        VALUES (?, ?, ?, ?)
        ''', (event_type, datetime.now(), person_detected, authorized))
        self.conn.commit()
