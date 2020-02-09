import Database
from tkinter import *
from functools import partial
import sqlite3
from sqlite3 import Error
import os
import random
import pyautogui
from datetime import datetime

class LoginWindow(Frame):
    def __init__(self, master=None): 
        Frame.__init__(self, master)
                
        self.master = master
        self.master.geometry("600x400")

        self.init_window()

    def init_window(self):
        self.master.title("Spending Tracker - Login")

        # Initialize window with necessary buttons and labels
        username_label = Label(self, text='Username: ')
        username_label.grid(row=1, column=1, sticky="N", padx=40, pady=20)
        username_entry = Entry(self, width=40)
        username_entry.grid(row=1, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        pass_label = Label(self, text='Password: ')
        pass_label.grid(row=2, column=1, sticky="N", padx=40, pady=20)
        pass_entry = Entry(self, show="*", width=40)
        pass_entry.grid(row=2, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        login_button = Button(self, text='Login', width=20, command=partial(self.processLogin, username_entry, pass_entry))
        login_button.focus_set()
        login_button.grid(row=3, column=2, columnspan=1, padx=10, pady=25)

        create_button = Button(self, text='Create Account', width=20, command=lambda: self.newWindow(CreateAccount))
        create_button.grid(row=4, column=2,pady=25)

        forgot_button = Button(self, text='Forgot Password', width=20)
        forgot_button.grid(row=5, column=2,pady=25)

    def processLogin(self, user, pw):
        username = user.get()
        password = pw.get()

        # Check if they have anything entered
        if not username or not password:
            MainApp.createAlert(self, "You must enter a username and password.", "Error", "OK")
            return
        
        # Check for valid username & password.  If EITHER are incorrect, say that EITHER are incorrect, not "user incorrect" or "pass incorrect"
        login_info = db.getLoginInfo()

        if username not in login_info.keys() or password not in login_info[username]:
            print("Username or password invalid.")
            MainApp.createAlert(self, "Username or password invalid.", "Error", "OK")
        elif username in login_info.keys() and password in login_info[username]:
            # If both valid
            MainApp.createAlert(self, "Login successful!", "Success!", "OK")
            db.CURRENT_USERNAME = username
            CURRENT_USERNAME = username
            user.delete(0, END)
            pw.delete(0, END)
            self.newWindow(MainApp)
            ### DESTROY LOGIN WINDOW SOMEHOW ###

    def newWindow(self, window):
        self.new = Toplevel(self.master)
        window(self.new)


class CreateAccount(Frame):
    def __init__(self, master): 
        Frame.__init__(self, master)
                
        self.master = master
        self.master.geometry("750x400")
        self.init_window()

    def init_window(self):
        self.master.title("Spending Tracker - Account Creation")
        self.pack(fill=BOTH, expand=1)

        # Initialize window with necessary buttons and labels
        username_label = Label(self, text='Username: ')
        username_label.grid(row=1, column=1, sticky="N", padx=40, pady=20)
        username_entry = Entry(self, width=40)
        username_entry.grid(row=1, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        pass_label = Label(self, text='Password: ')
        pass_label.grid(row=2, column=1, sticky="N", padx=40, pady=20)
        pass_entry = Entry(self, show="*", width=40)
        pass_entry.grid(row=2, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        email_label = Label(self, text='Email: ')
        email_label.grid(row=3, column=1, sticky="N", padx=40, pady=20)
        email_entry = Entry(self, width=40)
        email_entry.grid(row=3, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        threshold_label = Label(self, text='Monthly Spending Threshold: ')
        threshold_label.grid(row=4, column=1, sticky="NW", padx=40, pady=20)
        threshold_entry = Entry(self, width=10)
        threshold_entry.grid(row=4, column=2, sticky="NW", padx=40, pady=20, columnspan=2)

        create_button = Button(self, text='Create', width=20, command=partial(self.processCreation, username_entry, pass_entry, email_entry, threshold_entry))
        create_button.grid(row=5, column=2, padx=10, pady=25, sticky="W")

    def processCreation(self, user, pw, email, thresh):
        for item in [user.get(), pw.get(), email.get()]:
            if not item:
                print("Username, password, and email are required!")
                MainApp.createAlert(self, "Username, password, and email are required!", "Error", "OK")
                return
            
        login_info = db.getLoginInfo()
        if user.get() in login_info.keys():
            print("Username already taken.")
            MainApp.createAlert(self, "Username already taken.", "Error", "OK")
            return
        elif any(email.get() in val for val in login_info.values()):
            print("Email already in use.")
            MainApp.createAlert(self, "Email already in use.", "Error", "OK")
            return
        else:
            self.username = user.get()
            self.password = pw.get()
            self.email = email.get()
            self.date = datetime.now().strftime("%m/%d/%Y")
            self.threshold = thresh.get()

            values = (self.username, self.password, self.email, self.date, self.threshold)
            print(values)
            query = """INSERT INTO accounts VALUES (?, ?, ?, ?, ?);"""

            insertions = {values: query}

            insert = db.insertAccount(insertions)
            if insert is True:
                print("Account creation successful!")
                MainApp.createAlert(self, "Account creation successful!", "Success", "OK")
                self.master.destroy()
            else:
                print("Error with account creation.")


class ForgotPassword(Frame):
    def __init__(self, master): 
        Frame.__init__(self, master)
                
        self.master = master
        self.master.geometry("750x400")
        self.init_window()

    def init_window(self):
        self.master.title("Spending Tracker - Forgot Password")
        self.pack(fill=BOTH, expand=1)


class MainApp(Frame):

    def __init__(self, master): 
        Frame.__init__(self, master)
                
        self.master = master
        self.master.geometry("1080x600")

        self.all_ids = db.getDatabaseIds()

        # Initiate structures to dynamically store and delete widgets from dictionaries
        self.del_buttons = {}
        self.itemEntries = {}
        self.price_entries = {}
        self.date_entries = {}
        self.cat_menus = {}
        self.occupied_rows = []
        self.id = 0

        # Rollback dictionary to undo last submission
        self.rollback = {}

        # Get a free ID slot by checking against IDs in database
        while True:
            if self.id in self.all_ids:
                print("Starting ID already found in DB -- incrementing ID")
                self.id += 1
            else:
                break

        # Hold all records (entries) present in the window that are to be submitted to DB
        self.records = {}

        self.init_window()


    def init_window(self):     
        self.master.title("Spending Tracker")
        self.pack(fill=BOTH, expand=1)

        # Initialize window with necessary buttons and labels
        addEntryButton = Button(self, text='Add Entry', width=20, command=self.addEntry)
        addEntryButton.grid(row=0, column=0, padx=20, pady=25)

        submitButton = Button(self, text='Submit', width=20, command=self.insert)
        submitButton.grid(row=0, column=1, padx=20, pady=25)

        rollbackButton = Button(self, text='Undo Entries', width=20, command=partial(self.undo, self.rollback))
        rollbackButton.grid(row=0, column=2, padx=20, pady=25)

        summaryButton = Button(self, text='Summary', width=20, command=db.getSummary)
        summaryButton.grid(row=0, column=3, padx=20, pady=25)

        searchButton = Button(self, text='Search DB', width=20, command=db.customSearch)
        searchButton.grid(row=0, column=4, padx=20, pady=25)

        itemLabel = Label(self, text='Item', width=20)
        itemLabel.grid(row=1, column=1)

        priceLabel = Label(self, text='Price', width=20)
        priceLabel.grid(row=1, column=2)

        dateLabel = Label(self, text='Date', width=20)
        dateLabel.grid(row=1, column=3)

        catLabel = Label(self, text='Category', width=20)
        catLabel.grid(row=1, column=4)

        # CREATE FIRST ROW AT START
        var = StringVar(self) # for OptionMenu
        var.set("-empty-") # default value
        ent = Entry(self)
        ent.grid(row=2, column=1, sticky="WE", padx=15)
        price_entry = Entry(self, validate="key", validatecommand=(self.register(lambda x: (x.isdigit() or x == '.')), '%S'))
        price_entry.grid(row=2, column=2, stick="WE", padx=30)
        date_entry = Entry(self, validate="key", validatecommand=(self.register(lambda x: (x.isdigit() or x == '/')), '%S'))
        date_entry.grid(row=2, column=3, stick="WE", padx=30)
        cat_menu = OptionMenu(self, var, *["Bill", "Grocery", "Personal", "Other"])
        cat_menu.grid(row=2, column=4, stick="W", padx=30)

        self.checkID()

        print("Entry with id {} created".format(self.id))

        #self.occupied_rows.append(next_row)
        #self.del_buttons[self.id] = del_button
        self.itemEntries[self.id] = ent
        self.price_entries[self.id] = price_entry
        self.date_entries[self.id] = date_entry
        self.cat_menus[self.id] = [cat_menu, var]
        record = [ent, price_entry, date_entry, var]
        self.records[self.id] = record
        self.id += 1

    def undo(self, rb):
        if len(rb) == 0:
            self.createAlert("There are no entries submitted prior to this to undo.", "Nothing to undo", "OK")
            return
        else:
            text = ""
            for idx, record in rb.items():
                item = record[0]
                price = record[1]
                date = record[2]
                cat = record[3]
                text += "ID {}:  {}    {}    {}    {}\n".format(idx, item, price, date, cat)

            ans = pyautogui.confirm(text="Are you sure you want to delete the previous entries below?\n\n{}".format(text), title="Delete previous entries?", buttons=['Yes', 'No'])
            if ans == 'Yes':
                db.rollback(rb)
                self.rollback.clear()
            elif ans == 'No':
                return
    
    def checkID(self):
        self.all_ids = db.getDatabaseIds()
        # Get a free ID slot by checking against IDs in database
        while True:
            if self.id in self.all_ids:
                print("ID already found in DB -- incrementing before assigning.")
                self.id += 1
            else:
                return

    def addEntry(self):
        # A check for duplicate ID
        if self.id in self.itemEntries.keys():
            print("DUPLICATE ROW ID ERROR -- entry not created.")
            return

        # Check for already occupied rows in the grid before creation
        next_row = len(self.itemEntries) + 3 # +2 because of the first two rows already being occupied by the first two buttons before entry rows
        occupied = True
        while occupied:
            if next_row in self.occupied_rows:
                print("Row already taken -- incrementing row number.")
                next_row += 1
            else:
                occupied = False
 
        var = StringVar(self) # for OptionMenu
        var.set("-empty-") # default value

        del_button = Button(self, text="X", command=partial(self.deleteEntry, self.id))
        del_button.grid(row=next_row, column=0)

        ent = Entry(self)
        ent.grid(row=next_row, column=1, sticky="WE", padx=15)

        price_entry = Entry(self, validate="key", validatecommand=(self.register(lambda x: (x.isdigit() or x == '.')), '%S'))
        price_entry.grid(row=next_row, column=2, stick="WE", padx=30)

        date_entry = Entry(self, validate="key", validatecommand=(self.register(lambda x: (x.isdigit() or x == '/')), '%S'))
        date_entry.grid(row=next_row, column=3, stick="WE", padx=30)

        cat_menu = OptionMenu(self, var, *["Bill", "Grocery", "Personal", "Other"])
        cat_menu.grid(row=next_row, column=4, stick="W", padx=30)

        self.checkID()

        print("Entry with id {} created".format(self.id))
        
        self.occupied_rows.append(next_row)
        self.del_buttons[self.id] = del_button
        self.itemEntries[self.id] = ent
        self.price_entries[self.id] = price_entry
        self.date_entries[self.id] = date_entry
        self.cat_menus[self.id] = [cat_menu, var]
        record = [ent, price_entry, date_entry, var]
        self.records[self.id] = record
        self.id += 1


    def deleteEntry(self, idx):
        del_button = self.del_buttons[idx]
        ent = self.itemEntries[idx]
        price_entry = self.price_entries[idx]
        date_entry = self.date_entries[idx]
        cat_menu = self.cat_menus[idx]

        # Delete the record from records dictionary
        del self.records[idx]

        print("Entry with id {} deleted: {} - {} - {}".format(idx, ent.get(), price_entry.get(), cat_menu[1].get()))

        # Destroy the widgets
        del_button.destroy()
        ent.destroy()
        price_entry.destroy()
        date_entry.destroy()
        cat_menu[0].destroy()

        # Remove the widgets of the record from their respective dictionaries
        del self.del_buttons[idx]
        del self.itemEntries[idx]
        del self.price_entries[idx]
        del self.date_entries[idx]
        del self.cat_menus[idx]

    def checkDate(self):
        for idx, record in self.records.items():
            try:
                date = datetime.strptime(record[2].get(), '%m/%d/%Y')
            except:
                print("Improper date format in a date field!")
                self.createAlert("Improper date format in a date field. Expected format: mm/dd/yyyy", "Improper Date Format", "Ok, sorry")
                return False

    def insert(self):
        # Make sure dates are correct format before submission
        if self.checkDate() is False:
            return

        # Prep rollback dictionary for undo button
        for idx, record in self.records.items():
            self.rollback[idx] = [record[0].get(), record[1].get(), record[2].get(), record[3].get()]

        for idx, record in self.records.items():
            for i in range(4):
                if not record[i].get():
                    print("All fields must have a value!")
                    self.createAlert("All fields must have a value!", "Error", "OK")
                    return
                if i == 3:
                    if record[i].get() == "-empty-":
                        print("Categories must be something other than '-empty-'.")
                        self.createAlert("Categories must be something other than '-empty-'.", "Error", "OK")
                        return

        # Collect all records to be inserted into the database
        insertions = {}
        for idx, record in self.records.items():
            item = record[0].get()
            price = record[1].get()
            date = record[2].get()
            cat = record[3].get()
            username = db.CURRENT_USERNAME
            query = """INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?);"""
            values = (int(idx), str(item), float(price), str(date), str(cat), str(username))
            insertions[values] = query

        # Insert records into database by calling Database class
        result = db.insert(insertions)
        if result is False:
            print("Error with submitting these entries.")
            return
        else:
            # After submitting and inserting records to database, reset the rows
            self.resetWindow()


    def resetWindow(self):
        # Get the first ID in records (the first row), because it doesn't have an 'X' widget to delete
        first_id = next(iter(self.records))

        # Destroy the widgets in each row
        for idx, record in self.records.items():
            record[0].destroy()
            record[1].destroy()
            record[2].destroy()
            self.cat_menus[idx][0].destroy()
            if idx != first_id: # delete the 'X' widget if the row isn't the first
                self.del_buttons[idx].destroy()
        
        # Reset widget dictionaries and the records dict
        self.del_buttons = {}
        self.itemEntries = {}
        self.price_entries = {}
        self.date_entries = {}
        self.cat_menus = {}
        self.occupied_rows = []

        self.records = {}

        # CREATE FIRST ROW AT START
        var = StringVar(self) # for OptionMenu
        var.set("-empty-") # default value
        ent = Entry(self)
        ent.grid(row=2, column=1, sticky="WE", padx=15)
        price_entry = Entry(self, validate="key", validatecommand=(self.register(lambda x: (x.isdigit() or x == '.')), '%S'))
        price_entry.grid(row=2, column=2, stick="WE", padx=30)
        date_entry = Entry(self, validate="key", validatecommand=(self.register(lambda x: (x.isdigit() or x == '/')), '%S'))
        date_entry.grid(row=2, column=3, stick="WE", padx=30)
        cat_menu = OptionMenu(self,var, *["Bill", "Grocery", "Personal", "Other"])
        cat_menu.grid(row=2, column=4, stick="W", padx=30)

        #self.occupied_rows.append(next_row)
        #self.del_buttons[self.id] = del_button
        self.itemEntries[self.id] = ent
        self.price_entries[self.id] = price_entry
        self.date_entries[self.id] = date_entry
        self.cat_menus[self.id] = [cat_menu, var]
        record = [ent, price_entry, date_entry, var]
        self.records[self.id] = record
        self.id += 1

    def createAlert(self, text, title, button):
        pyautogui.alert(text=text, title=title, button=button)

    def client_exit(self):
        db.conn.close()
        exit()

if __name__ == "__main__":
    root = Tk()

    #root.geometry("1080x600")
    root.resizable(False, False)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    app = LoginWindow(root).grid(sticky="NSEW")

    # Who is logged in
    CURRENT_USERNAME = ""

    # Initialize database at startup
    db = Database.Database()

    root.mainloop()
