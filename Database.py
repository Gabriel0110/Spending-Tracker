import sqlite3
from sqlite3 import Error
import os
import pyautogui
from datetime import datetime

class Database:
    def __init__(self):
        # Connect to a database, or create + connect at startup
        cwd = os.getcwd()
        self.conn = self.create_connection(cwd + "/spending_db.db")

        self.create_expenses_table = """CREATE TABLE IF NOT EXISTS expenses (
                                        id INTEGER PRIMARY KEY,
                                        item VARCHAR(40) NOT NULL,
                                        price FLOAT NOT NULL,
                                        date VARCHAR(10) NOT NULL,
                                        category VARCHAR(20) NOT NULL
                                    ); """

        if self.conn is not None:
            self.create_table(self.conn, self.create_expenses_table)
        else:
            print("Error -- no database connection found.")
            pyautogui.alert(text = "Error -- no database connection found.", title = "ERROR", button = 'OK')

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print("Database connection successful!")
            return conn
        except Error as e:
            print(e)
            pyautogui.alert(text = e, title = "ERROR", button = 'OK')
    
        return conn

    def create_table(self, conn, create_table):
        try:
            c = conn.cursor()
            c.execute(create_table)
        except Error as e:
            print(e)
            pyautogui.alert(text = e, title = "ERROR", button = 'OK')

    def insert(self, insertions):
        c = self.conn.cursor()

        # Loop through all records (entries), inserting each into the database
        for values, query in insertions.items():
            try:
                c.execute(query, values)
                print("Insertion successful!")
            except Error as e:
                print(e)
                pyautogui.alert(text = e, title = "ERROR", button = ['OK'])
                return
        pyautogui.alert(text = "Insertions successful!", title = "SUCCESS", button = 'OK')
        self.conn.commit()

    def getDatabaseIds(self):
        c = self.conn.cursor()
        try:
            id_col = c.execute("""SELECT id FROM expenses""")
            ids = [idx[0] for idx in id_col]
            #print(ids)
            return ids
        except Error as e:
            print("Could not get Database IDs: {}".format(e))
            pyautogui.alert(text = e, title = "ERROR", button = 'OK')
            return

    def getSummary(self):
        current_month = datetime.now().month
        #current_year = datetime.now().year

        c = self.conn.cursor()
        db_avg_price = c.execute("""SELECT AVG(price) FROM expenses""").fetchone()
        db_max_price = c.execute("""SELECT MAX(price) FROM expenses""").fetchone()
        db_min_price = c.execute("""SELECT MIN(price) FROM expenses""").fetchone()
        db_sum_price = c.execute("""SELECT SUM(price) FROM expenses""").fetchone()

        if current_month in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            current_month = "0{}".format(current_month)
        current_month_avg = c.execute("""SELECT AVG(price) FROM expenses WHERE date LIKE ?""", (current_month+"%",)).fetchone()
        current_month_max = c.execute("""SELECT MAX(price) FROM expenses WHERE date LIKE ?""", (current_month+"%",)).fetchone()
        current_month_min = c.execute("""SELECT MIN(price) FROM expenses WHERE date LIKE ?""", (current_month+"%",)).fetchone()
        current_month_sum = c.execute("""SELECT SUM(price) FROM expenses WHERE date LIKE ?""", (current_month+"%",)).fetchone()

        if current_month_sum == (None,):
            month_summary = "[*] No data for this month!\n"
        else:
            month_summary = "[*] This month:\n\
            - Average price: ${:.2f}\n\
            - Max price: ${:.2f}\n\
            - Minimum price: ${:.2f}\n\
            - Total: ${:.2f}".format(current_month_avg[0], current_month_max[0], current_month_min[0], current_month_sum[0])

        if db_sum_price == (None,):
            db_summary = "[*] There are no price entries in this database!"
        else:
            db_summary = "[*] Overall:\n\
            - Average price: ${:.2f}\n\
            - Max price: ${:.2f}\n\
            - Minimum price: ${:.2f}\n\
            - Total: ${:.2f}".format(db_avg_price[0], db_max_price[0], db_min_price[0], db_sum_price[0])

        total_summary = month_summary + "\n\n" + db_summary
        pyautogui.alert(text=total_summary, title="Summary", button="OK")

    def customSearch(self):
        # ONLY ACCEPTS SQL AT THE MOMENT -- human language conversion coming soon :(
        query = pyautogui.prompt(text="Here's an example query: 'get sum of prices on the 1st of this month'\n\nEnter your search query:", title="Search Database", default="get sum of prices on the 1st of this month")
        if query is None:
            return

        for action in ['delete', 'drop', 'insert', 'update', 'replace']:
            if action in query.lower():
                pyautogui.alert(text="Sorry - you can only SELECT from the database", title="Oops", button="OK")
                return
        
        # Manipulate string to identify what keywords are in there, then convert keywords to SQL
        #action = "SELECT"
        #function = "SUM"
        #what = "price"
        #where = "expenses"
        #when = "WHERE date LIKE MM/01/YYYY"

        c = self.conn.cursor()
        results = c.execute(query).fetchall()
        pyautogui.alert(text="Search results:\n{}".format(results[0]), title="Search Results", button="OK")

    def rollback(self):
        return