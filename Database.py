import Spending_Tracker
import sqlite3
from sqlite3 import Error
import os
import pyautogui
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.CURRENT_USERNAME = ""

        # Connect to a database, or create + connect at startup
        cwd = os.getcwd()

        self.conn = self.create_connection(cwd + "/spending_db.db")

        self.create_expenses_table = """CREATE TABLE IF NOT EXISTS expenses (
                                        id INTEGER PRIMARY KEY,
                                        item VARCHAR(40) NOT NULL,
                                        price FLOAT NOT NULL,
                                        date VARCHAR(10) NOT NULL,
                                        category VARCHAR(20) NOT NULL,
                                        username VARCHAR(40) NOT NULL
                                    ); """

        self.create_accounts_table = """CREATE TABLE IF NOT EXISTS accounts (
                                        username VARCHAR(100) PRIMARY KEY,
                                        password VARCHAR(100) NOT NULL,
                                        email VARCHAR(100) NOT NULL,
                                        creation_date VARCHAR(10) NOT NULL,
                                        price_threshold FLOAT
                                    ); """

        if self.conn is not None:
            self.create_tables(self.conn, [self.create_expenses_table, self.create_accounts_table])
        else:
            print("Error -- no database connection found.")
            Spending_Tracker.MainApp.createAlert(self, "Error -- no database connection found.", "ERROR", "OK")
            exit()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print("Database connection successful!")
            return conn
        except Error as e:
            print(e)
            Spending_Tracker.MainApp.createAlert(self, e, "ERROR", "OK")    
        return conn

    def create_tables(self, conn, tables):
        c = conn.cursor()
        for table in tables:
            try:
                c.execute(table)
            except Error as e:
                print(e)
                Spending_Tracker.MainApp.createAlert(self, e, "ERROR", "OK")

    def insert(self, insertions):
        c = self.conn.cursor()

        # Loop through all records (entries), inserting each into the database
        for values, query in insertions.items():
            try:
                c.execute(query, values)
                print("Insertion successful!")
                
                # Check if breach threshold
                breached, user_threshold = self.checkThreshold(c)
                if breached:
                    print("User exceeded monthly spending theshold!")
                    Spending_Tracker.MainApp.createAlert(self, "You have exceeded your monthly spending threshold of ${:.2f}!".format(float(user_threshold)), "Threshold exceeded!", "Oops!")
            except Error as e:
                print(e)
                Spending_Tracker.MainApp.createAlert(self, e, "ERROR", "OK")
                return False
        #pyautogui.alert(text = "Insertions successful!", title = "SUCCESS", button = 'OK')
        self.conn.commit()
        return True

    def insertAccount(self, insertions):
        c = self.conn.cursor()

        # Loop through all records (entries), inserting each into the database
        for values, query in insertions.items():
            try:
                c.execute(query, values)
                print("Insertion successful!")
            except Error as e:
                print(e)
                Spending_Tracker.MainApp.createAlert(self, e, "ERROR", "OK")
                return False
        #pyautogui.alert(text = "Insertions successful!", title = "SUCCESS", button = 'OK')
        self.conn.commit()
        return True

    def checkThreshold(self, c):
        current_month = self.getCurrentMonth()
        user_threshold = c.execute("""SELECT price_threshold FROM accounts WHERE username = ?""", (self.CURRENT_USERNAME,)).fetchone()[0]
        monthly_sum = c.execute("""SELECT SUM(price) FROM expenses WHERE username = ? AND date LIKE ? AND category != ?""", (self.CURRENT_USERNAME, current_month+"%", "Bill",)).fetchone()[0]

        if user_threshold is None:
            return False, None

        if (0 if monthly_sum is None else monthly_sum) > user_threshold:
            return True, user_threshold
        else:
            return False, user_threshold

    def getDatabaseIds(self):
        c = self.conn.cursor()
        try:
            id_col = c.execute("""SELECT id FROM expenses""")
            ids = [idx[0] for idx in id_col]
            #print(ids)
            return ids
        except Error as e:
            print("Could not get Database IDs: {}".format(e))
            Spending_Tracker.MainApp.createAlert(self, e, "ERROR", "OK")
            return

    def getLoginInfo(self):
        c = self.conn.cursor()
        try:
            info = c.execute("""SELECT username, password, email FROM accounts""").fetchall()

            info_dict = {}
            for (user, pw, email) in info:
                info_dict[user] = [pw, email]
            print(info_dict)
            return info_dict
        except Error as e:
            print(e)
            Spending_Tracker.MainApp.createAlert(self, e, "ERROR", "OK")

    def getSummary(self):
        current_month = self.getCurrentMonth()
        #current_year = datetime.now().year

        c = self.conn.cursor()
        db_avg_price = c.execute("""SELECT AVG(price) FROM expenses WHERE username = ?""", (self.CURRENT_USERNAME,)).fetchone()
        db_max_price = c.execute("""SELECT MAX(price) FROM expenses WHERE username = ?""", (self.CURRENT_USERNAME,)).fetchone()
        db_min_price = c.execute("""SELECT MIN(price) FROM expenses WHERE username = ?""", (self.CURRENT_USERNAME,)).fetchone()
        db_sum_price = c.execute("""SELECT SUM(price) FROM expenses WHERE username = ?""", (self.CURRENT_USERNAME,)).fetchone()

        current_month_avg = c.execute("""SELECT AVG(price) FROM expenses WHERE username = ? AND date LIKE ?""", (self.CURRENT_USERNAME, current_month+"%",)).fetchone()
        current_month_max = c.execute("""SELECT MAX(price) FROM expenses WHERE username = ? AND date LIKE ?""", (self.CURRENT_USERNAME, current_month+"%",)).fetchone()
        current_month_min = c.execute("""SELECT MIN(price) FROM expenses WHERE username = ? AND date LIKE ?""", (self.CURRENT_USERNAME, current_month+"%",)).fetchone()
        current_month_sum = c.execute("""SELECT SUM(price) FROM expenses WHERE username = ? AND date LIKE ?""", (self.CURRENT_USERNAME, current_month+"%",)).fetchone()

        month_price, month_cat, overall_price, overall_cat = self.getPriciestCategory(c, current_month)

        if current_month_sum == (None,):
            month_summary = "[*] No data for this month!\n"
        else:
            month_summary = "[*] This month:\n\
            - Average price: ${:.2f}\n\
            - Maximum price: ${:.2f}\n\
            - Minimum price: ${:.2f}\n\
            - Total: ${:.2f}\n\
            - Most expensive category: {} with ${:.2f}\n".format(current_month_avg[0], current_month_max[0], current_month_min[0], current_month_sum[0], month_cat, month_price)

        if db_sum_price == (None,):
            db_summary = "[*] There are no price entries in this database!"
        else:
            db_summary = "[*] Overall:\n\
            - Average price: ${:.2f}\n\
            - Maximum price: ${:.2f}\n\
            - Minimum price: ${:.2f}\n\
            - Total: ${:.2f}\n\
            - Most expensive category: {} with ${:.2f}".format(db_avg_price[0], db_max_price[0], db_min_price[0], db_sum_price[0], overall_cat, overall_price)

        total_summary = month_summary + "\n\n" + db_summary
        pyautogui.alert(text=total_summary, title="Summary", button="OK")
        self.displayGraph()

    def displayGraph(self):
        import matplotlib.pyplot as plt

        prior_thirty = []
        for i in range(31):
            date = (datetime.now() + timedelta(-(i+1))).strftime("%m/%d/%Y")
            prior_thirty.append(date)
        prior_thirty = prior_thirty[::-1] # in order from 30 days ago, to yesterday

        # Get sum of money spent per category in last 30 days
        cat_sums = {"Bill": 0, "Grocery": 0, "Personal": 0, "Other": 0}
        c = self.conn.cursor()
        for date in prior_thirty:
            for cat in ["Bill", "Grocery", "Personal", "Other"]:
                cat_sum = c.execute("""SELECT SUM(price) FROM expenses WHERE date = ? AND category = ?""", (date, cat)).fetchone()[0]
                cat_sums[cat] += (0 if cat_sum is None else (float(cat_sum)))

        plt.bar(cat_sums.keys(), cat_sums.values())
        plt.xticks(["Bill", "Grocery", "Personal", "Other"])
        plt.ylabel('Dollar Amount')
        plt.xlabel('Category')
        plt.title('Total Spent Per Category in Last 30 Days')
        plt.show()
        return

    def getPriciestCategory(self, c, current_month):
        categories = ["Bill", "Grocery", "Personal", "Other"]
        monthly_sums = {}
        overall_sums = {}
        for cat in categories:
            month_sum = c.execute("""SELECT SUM(price) FROM expenses WHERE username = ? AND category = ? AND date LIKE ?""", (self.CURRENT_USERNAME, cat, current_month+"%",)).fetchone()
            overall_sum = c.execute("""SELECT SUM(price) FROM expenses WHERE username = ? AND category = ?""", (self.CURRENT_USERNAME, cat,)).fetchone()
            monthly_sums[cat] = (float(month_sum[0]) if month_sum[0] else 0)
            overall_sums[cat] = (float(overall_sum[0]) if overall_sum[0] else 0)
            print("Monthly: Category {} with ${}".format(cat, month_sum[0]))
            print("Overall: Category {} with ${}".format(cat, overall_sum[0]))

        month_cat = max(monthly_sums, key=lambda key: monthly_sums[key])
        month_max = monthly_sums[month_cat]
        overall_cat = max(overall_sums, key=lambda key: overall_sums[key])
        overall_max = overall_sums[overall_cat]

        # month_index = None
        # overall_index = None
        # month_max = 0
        # overall_max = 0
        # for i in range(4):
        #     if (monthly_sums[i] if monthly_sums[i] else 0) > month_max:
        #         month_index = i
        #         month_max = monthly_sums[i]
        #     elif (monthly_sums[i] if monthly_sums[i] else 0) == month_max:
        #         month_index = i

        #     if (overall_sums[i] if overall_sums[i] else 0) > overall_max:
        #         overall_index = i
        #         overall_max = overall_sums[i]
        #     elif (overall_sums[i] if overall_sums[i] else 0) == overall_max:
        #         overall_index = i
                
        return [month_max, month_cat, overall_max, overall_cat]

    def getCurrentMonth(self):
        current_month = datetime.now().month
        if current_month in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            current_month = "0{}".format(current_month)
        else:
            current_month = str(current_month)
        return current_month

    def customSearch(self):
        # ONLY ACCEPTS SQL AT THE MOMENT -- human language conversion coming soon :(
        query = pyautogui.prompt(text="Here's an example query: 'get sum of prices on the 1st of this month'\n\nEnter your search query:", title="Search Database", default="get sum of prices on the 1st of this month")
        if query is None:
            return

        for action in ['delete', 'drop', 'insert', 'update', 'replace']:
            if action in query.lower():
                Spending_Tracker.MainApp.createAlert(self, "Sorry - you can only SELECT from the database", "Oops", "OK")
                return
        
        # Manipulate string to identify what keywords are in there, then convert keywords to SQL
        #action = "SELECT"
        #function = "SUM"
        #what = "price"
        #where = "expenses"
        #when = "WHERE date LIKE MM/01/YYYY"

        query += """ WHERE username = ?"""

        c = self.conn.cursor()
        results = c.execute(query, (self.CURRENT_USERNAME,)).fetchall()
        Spending_Tracker.MainApp.createAlert(self, "Search results:\n{}".format(results[0]), "Search Results", "OK")

    def rollback(self, rb):
        c = self.conn.cursor()
        for idx in rb.keys():
            try:
                c.execute("""DELETE FROM expenses WHERE id = ?""", (idx,))
                print("Successfully removed last entries.")
            except Error as e:
                print(e)
                Spending_Tracker.MainApp.createAlert(self, e, "Error", "OK")
                return
        Spending_Tracker.MainApp.createAlert(self, "Successfully removed last created entries.", "Success", "OK")

