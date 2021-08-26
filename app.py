# Import modules needed
import sqlite3
from flask import Flask, request, jsonify


# putting all the tables in a class
class QatTables:
    def __init__(self):
        self.connect = sqlite3.connect('QAT_Motors.db')    # connecting sqlite3 to the database called QAT_Motors
        self.cursor = self.connect.cursor()

        # creating a table for admin
        self.connect.execute("CREATE TABLE IF NOT EXISTS Admin(Fullname TEXT NOT NULL,"   # command to create the table
                             "Username TEXT NOT NULL PRIMARY KEY,"
                             "Password TEXT NOT NULL)")
        print("Admin table created successfully")    # checking if table was created

        # creating a table for clients to register
        self.connect.execute("CREATE TABLE IF NOT EXISTS Clients(Name TEXT NOT NULL,"   # command to create the table
                             "Surname TEXT NOT NULL,"
                             "Email TEXT NOT NULL,"
                             "Cell TEXT NOT NULL,"
                             "Address TEXT NOT NULL,"
                             "Username TEXT NOT NULL PRIMARY KEY,"
                             "Password TEXT NOT NULL)")
        print("Clients table created successfully")    # checking if table was created

        # creating a table for clients to register their vehicles
        self.connect.execute("CREATE TABLE IF NOT EXISTS Vehicles(Type TEXT NOT NULL,"   # command to create the table
                             "Year_Modal TEXT NOT NULL,"
                             "VIN_Numb TEXT NOT NULL,"
                             "Reg_Numb TEXT NOT NULL PRIMARY KEY,"
                             "Username TEXT NOT NULL,"
                             "CONSTRAINT fk_Clients FOREIGN KEY (Username) REFERENCES Clients (Username))")
        print("Vehicles table created successfully")    # checking if table was created

        # creating a table for the services provided
        self.connect.execute("CREATE TABLE IF NOT EXISTS Services(Service_Numb INTEGER PRIMARY KEY AUTOINCREMENT,"
                             "Type TEXT NOT NULL UNIQUE,"
                             "Description TEXT NOT NULL,"
                             "Duration TEXT NOT NULL,"
                             "Price TEXT NOT NULL)")
        print("Services table created successfully")

        # creating a table for cars to book in
        self.connect.execute("CREATE TABLE IF NOT EXISTS Appointments(Reg_Numb TEXT NOT NULL, "
                             "Type TEXT NOT NULL,"
                             "Day TEXT NOT NULL,"
                             "Time TEXT NOT NULL PRIMARY KEY,"
                             "CONSTRAINT fk_Vehicles FOREIGN KEY (Reg_Numb) REFERENCES Vehicles (Reg_Numb)"
                             "CONSTRAINT fk_Services FOREIGN KEY (Type) REFERENCES Services (Type))")
        print("Appointments table created successfully")

        self.connect.close()    # closes connection to database


QatTables()     # calling the class

# starting the Flask app
app = Flask(__name__)   # allows you to use api
app.debug = True    # when finds a bug, it continues to run
