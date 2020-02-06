import Database
from tkinter import *
from functools import partial
import sqlite3
from sqlite3 import Error
import os
import random
import pyautogui
from datetime import datetime
        

class Window(Frame):

    def __init__(self, master=None): 
        Frame.__init__(self, master)
                
        self.master = master
        self.DB = Database.Database() # init database at startup

        self.all_ids = self.DB.getDatabaseIds()

        # Initiate structures to dynamically store and delete widgets from dictionaries
        self.del_buttons = {}
        self.itemEntries = {}
        self.price_entries = {}
        self.date_entries = {}
        self.cat_menus = {}
        self.occupied_rows = []
        self.id = 0

        # Get a free ID slot by checking against IDs in database
        while True:
            if self.id in self.all_ids:
                print("Starting ID already found in DB -- incrementing ID")
                self.id += 1
            else:
                break

        # Hold all records (entries) present in the window
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

        rollbackButton = Button(self, text='Rollback (INACTIVE)', width=20, command=self.DB.rollback)
        rollbackButton.grid(row=0, column=2, padx=20, pady=25)

        summaryButton = Button(self, text='Summary', width=20, command=self.DB.getSummary)
        summaryButton.grid(row=0, column=3, padx=20, pady=25)

        searchButton = Button(self, text='Search DB', width=20, command=self.DB.customSearch)
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

    
    def checkID(self):
        self.all_ids = self.DB.getDatabaseIds()
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

        cat_menu = OptionMenu(self, var, *["Tech", "Groceries", "Personal", "Misc."])
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


    def insert(self):
        # Collect all records to be inserted into the database
        insertions = {}
        for idx, record in self.records.items():
            item = record[0].get()
            price = record[1].get()
            date = record[2].get()
            cat = record[3].get()
            query = """INSERT INTO expenses VALUES (?, ?, ?, ?, ?);"""
            values = (int(idx), str(item), float(price), str(date), str(cat))
            insertions[values] = query

        # Insert records into database by calling Database class
        self.DB.insert(insertions)

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
        cat_menu = OptionMenu(self,var, *["Tech", "Groceries", "Personal", "Misc."])
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


    def client_exit(self):
        self.DB.conn.close()
        exit()

root = Tk()

root.geometry("1080x600")
root.resizable(False, False)

app = Window(root)

root.mainloop()
