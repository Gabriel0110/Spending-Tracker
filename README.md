# Spending Tracker v1.0
A personal spending tracker to log and keep track of what I'm spending.

Includes a login and account creation page as well as local SQL database storage for accounts and spending data.

On creation of accounts, you can set your monthly spending threshold. If you're monthly total ever becomes greater than you're threshold, you will be alerted to this spending breach.

You can get a summary report of your spending data for the current month and overall. The summary includes a graph of expenses per category of items purchased to give you a visualization of where most of your spending is put towards.


## Can you test it?
Absolutely! You can clone the repository to your machine and run Spending_Tracker.py.

Note I: be sure to have the necessary libraries installed before running the program (only two are not from the Python standard library: sqlite3 and pyautogui).

Note II: the local database file is created wherever your current working directory is. So if you're in the Spending-Tracker folder to run the program, the database file should be created there.


## Features Currently Implemented:
- Local SQL database storage
- Account creation and login system
- Alerting for monthly budget threshold breach
- Submit multiple items at once
- Undo/Rollback function in case of entry mistakes
- Summary report function including current month and overall spending stats, and a graph of expenses per category in current month
- Ability to query the database to search for data (SELECT only) -- currently only SQL capable, but there will be human language conversion into SQL


## "I found a bug!"
Great! I'd love to know of any bugs found during testing or personal use so I can squash them like the bugs they are :)


## Spending Tracker v2.0 coming soon with a fresh, new user interface and interactions. Stay tuned...