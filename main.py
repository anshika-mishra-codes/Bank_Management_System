import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Your password"
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS BankDB")
conn.database = "BankDB"

create_customers_table = """
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    address VARCHAR(100)
)
"""

cursor.execute(create_customers_table)

create_accounts_table = """
CREATE TABLE IF NOT EXISTS Accounts (
    account_id INT PRIMARY KEY,
    customer_id INT,
    account_type VARCHAR(20),
    balance DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
)
"""

cursor.execute(create_accounts_table)

create_transactions_table = """
CREATE TABLE IF NOT EXISTS BankTransactions (
    transaction_id INT PRIMARY KEY,
    account_id INT,
    transaction_type VARCHAR(20),
    amount DECIMAL(10,2),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
)
"""

cursor.execute(create_transactions_table)

cursor.execute("""
ALTER TABLE BankTransactions
MODIFY transaction_id INT AUTO_INCREMENT
""")

insert_customer = """
INSERT IGNORE INTO Customers (customer_id, name, phone, address)
VALUES (%s, %s, %s, %s)
"""

customer_data = [
    (1, "Anshu", "9876543210", "Sultanpur"),
    (2, "Riya", "9876543211", "Lucknow"),
    (3, "Mahek", "9876543212", "Ayodhya")
]

cursor.executemany(insert_customer, customer_data)

conn.commit()

insert_account = """
INSERT IGNORE INTO Accounts (account_id, customer_id, account_type, balance)
VALUES (%s, %s, %s, %s)
"""

account_data = [
    (101, 1, "Savings", 5000),
    (102, 2, "Savings", 3000),
    (103, 3, "Current", 10000)
]

cursor.executemany(insert_account, account_data)

conn.commit()


insert_transaction = """
INSERT IGNORE INTO BankTransactions
(transaction_id, account_id, transaction_type, amount)
VALUES (%s, %s, %s, %s)
"""

transaction_data = [
    (1, 101, "Deposit", 2000),
    (2, 102, "Deposit", 1500),
    (3, 103, "Withdrawal", 1000)
]

cursor.executemany(insert_transaction, transaction_data)

conn.commit()

def get_integer(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid number 🔢")

def get_amount(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid amount 💵")

def deposit_money():
    account_id = get_integer("\nEnter account ID: ")

    cursor.execute(
        "SELECT account_id FROM Accounts WHERE account_id = %s",
        (account_id,)
    )

    account = cursor.fetchone()

    if account is None:
        print("Account not found, you need to create your account first! 👀")
        print ("Choose 1 from the menu.")
        return

    while True:
     amount =  get_amount("Enter deposit amount: ")
    
     if amount <= 0:
        print("Deposit amount must be greater than 0")
        continue
     
     break

    cursor.execute(
        "UPDATE Accounts SET balance = balance + %s WHERE account_id = %s",
        (amount, account_id)
    )

    cursor.execute(
        """
        INSERT INTO BankTransactions
        (account_id, transaction_type, amount)
        VALUES (%s, %s, %s)
        """,
        (account_id, "Deposit", amount)
    )

    conn.commit()

    print("\nDeposit successful,Your money has been added to the account.✨")


def withdraw_money():
    account_id = get_integer("\nEnter account ID: ")

    cursor.execute(
        "SELECT balance FROM Accounts WHERE account_id = %s",
        (account_id,)
    )

    balance = cursor.fetchone()

    if balance is None:
        print("Account not found! You need to create an account first!👀")
        return

    while True:
        amount =  get_amount("\nEnter withdrawal amount: ")

        if amount <= 0:
         print("Come on, Withdrawal amount must be more than Zero 🙄")
         continue

        if amount > balance[0]:
         print("You don't have enough money for this withdrawal 💳")
         continue

        break

    cursor.execute(
        "UPDATE Accounts SET balance = balance - %s WHERE account_id = %s",
        (amount, account_id)
    )

    cursor.execute(
        """
        INSERT INTO BankTransactions
        (account_id, transaction_type, amount)
        VALUES (%s, %s, %s)
        """,
        (account_id, "Withdrawal", amount)
    )

    conn.commit()

    print("Withdrawal successful, Your money is on its way💸 (imaginary)")


def check_balance():
    account_id = get_integer("\nEnter account ID: ")

    cursor.execute(
        "SELECT balance FROM Accounts WHERE account_id = %s",
        (account_id,)
    )

    balance = cursor.fetchone()

    if balance is None:
        print("Account not found! this account does not exist.")
        return

    print("\nCurrent balance:", balance[0])

def view_transactions():
    account_id = get_integer("\nEnter account ID: ")
    cursor.execute(
    "SELECT account_id FROM Accounts WHERE account_id = %s",
    (account_id,)
    )

    account = cursor.fetchone()
    if account is None:
        print("Account not found! You need to create an account first! 👀")
        return

    cursor.execute(
        """
        SELECT transaction_id, transaction_type, amount, transaction_date
        FROM BankTransactions
        WHERE account_id = %s
        """,
        (account_id,)
    )

    transactions = cursor.fetchall()

    if not transactions:
        print("No transactions found!")
        return

    for transaction in transactions:
       transaction_id, transaction_type, amount, transaction_date = transaction
       print("Transaction ID:", transaction_id, "| Type:", transaction_type, "| Amount: ₹", amount, "| Date & Time:", transaction_date)

def create_account():
    name = input("\nEnter customer name: ")
    phone = input("Enter phone number (10 digits): ")

    while len(phone) != 10 or not phone.isdigit():
        print("\nOops, a phone number has 10 digits buddy🙃")
        phone = input("\nEnter phone number (10 digits): ")
    address = input("Enter address: ")
    
    while True:
        account_type = input("Enter account type (Savings/Current): ").strip().title()
        if account_type in ("Savings", "Current"):
            break
        print("Please enter either Savings or Current 👀")

    cursor.execute("SELECT MAX(customer_id) FROM Customers")
    customer_id = cursor.fetchone()[0]

    if customer_id is None:
        customer_id = 1
    else:
        customer_id += 1

    cursor.execute(
        """
        INSERT INTO Customers (customer_id, name, phone, address)
        VALUES (%s, %s, %s, %s)
        """,
        (customer_id, name, phone, address)
    )

    cursor.execute("SELECT MAX(account_id) FROM Accounts")
    account_id = cursor.fetchone()[0]

    if account_id is None:
        account_id = 101
    else:
        account_id += 1

    cursor.execute(
        """
        INSERT INTO Accounts
        (account_id, customer_id, account_type, balance)
        VALUES (%s, %s, %s, %s)
        """,
        (account_id, customer_id, account_type, 0)
    )

    conn.commit()

    print("\nAccount created successfully! ✨")
    print("Your account ID is:", account_id)
    print("\n 🎀 Please note your account ID, you will need it for further operations.🎀")

while True:
    print("\n🌸 Welcome to the Bank 🌸")
    print("1. Create Account")
    print("2. Deposit Money")
    print("3. Withdraw Money")
    print("4. Check Balance")
    print("5. View Transactions")
    print("6. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        create_account()
        input("\nPress Enter to continue...")

    elif choice == "2":
        deposit_money()
        input("\nPress Enter to continue...")

    elif choice == "3":
        withdraw_money()
        input("\nPress Enter to continue...")

    elif choice == "4":
        check_balance()
        input("\nPress Enter to continue...")

    elif choice == "5":
        view_transactions()
        input("\nPress Enter to continue...")

    elif choice == "6":
        print("\nThanks for banking with us, have a good one...xoxo 🎀")
        break

    else:
        print("\nLooks like that's not an option. Try again✨")
        input("\nPress Enter to continue...")

cursor.close()
conn.close()