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


## Features in the Pipeline to be Implemented:
- Forgot Password button functionality (the button is not operable)
- A button for each entry to let the user add a note for that entry
- An estimated spending total for the next month, once an adequate amount of data is present. Likely run linear regression over the previous 30 days.
- A profile/settings button to allow the user to change their monthly spending threshold, password, and email any time they please.
- Add security questions to account creation for use in recovering or resetting passwords.
- Destroy login window on successful login
- Finish database searching functionality -- namely, conversion of human language to SQL by use of keyword search/regex
- A logging system that will log just about every action that takes place on the front end and back end, with timestamps. This will allow for better troubleshooting of issues with traceability.
- Add a quantity box for each entry, auto-filled with '1', but can be changed to alter the total price, in case of multiples of the same item
- And any more that continue to come to my mind as I develop...


## "I found a bug!"
Great! I'd love to know of any bugs found during testing or personal use so I can squash them like the bugs they are :)



### Spending Tracker v2.0 coming soon with a fresh, new user interface and interactions. Stay tuned...