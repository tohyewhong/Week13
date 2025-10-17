
import sqlite3
import os
from ..utils.config import settings

class SQLAgent:
    def __init__(self):
        os.makedirs(os.path.dirname(settings.SQL_DB_PATH), exist_ok=True)
        self.con = sqlite3.connect(settings.SQL_DB_PATH)

    def seed_demo(self):
        # Clear existing data and recreate tables
        self.con.execute("DROP TABLE IF EXISTS sales;")
        self.con.execute("DROP TABLE IF EXISTS employees;")
        self.con.execute("DROP TABLE IF EXISTS products;")
        
        # Sales table
        self.con.execute("CREATE TABLE sales(id INTEGER, item VARCHAR, qty INTEGER, price FLOAT);")
        self.con.execute("INSERT INTO sales VALUES (1,'apple',2,1.2),(2,'pear',5,2.5),(3,'apple',3,1.2),(4,'banana',10,0.8),(5,'orange',7,1.5),(6,'grape',3,2.8);")
        
        # Employees table
        self.con.execute("CREATE TABLE employees(id INTEGER, name VARCHAR, department VARCHAR, salary FLOAT);")
        self.con.execute("INSERT INTO employees VALUES (1,'Alice Johnson','IT',75000),(2,'Bob Smith','Marketing',65000),(3,'Carol Davis','IT',80000),(4,'David Wilson','Sales',60000),(5,'Eva Brown','Marketing',70000);")
        
        # Products table
        self.con.execute("CREATE TABLE products(id INTEGER, name VARCHAR, category VARCHAR, stock INTEGER, price FLOAT);")
        self.con.execute("INSERT INTO products VALUES (1,'Laptop','Electronics',50,999.99),(2,'Mouse','Electronics',200,25.50),(3,'Notebook','Stationery',500,3.99),(4,'Pen','Stationery',1000,1.99),(5,'Monitor','Electronics',75,299.99);")
        
        # Commit all changes
        self.con.commit()

    def run(self, sql: str):
        cursor = self.con.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
