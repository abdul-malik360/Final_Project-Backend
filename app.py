# Import modules needed
import sqlite3
from flask import Flask, request


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


@app.route('/admin', methods=["POST", "GET"])   # created a route that has both get and post methods
def admin():    # function for all admin uses
    response = {}   # making response an empty dictionary

    if request.method == "POST":    # if the function is post the following code happen
        fullname = request.form['Fullname']
        username = request.form['Username']
        password = request.form['Password']

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("INSERT INTO Admin("     # code that adds data to the table
                           "Fullname,"
                           "Username,"
                           "Password) VALUES(?, ?, ?)", (fullname, username, password))
            connect.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response

    if request.method == "GET":    # if the function is post the following code happen
        response = {}

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM Admin")

            admin_users = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = admin_users
        return response


@app.route('/admin/<username>', methods=["PUT", "GET"])
def edit_admin(username):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect("QAT_Motors.db") as connect:
            incoming_data = dict(request.json)
            new_data = {}

            if incoming_data.get("Fullname") is not None:
                new_data["Fullname"] = incoming_data.get("Fullname")
                with sqlite3.connect("QAT_Motors.db") as connect:
                    cursor = connect.cursor()
                    cursor.execute("UPDATE Admin SET Fullname =? WHERE Username=?", (new_data["Fullname"], username))
                    connect.commit()
                    response['Fullname'] = "Fullname Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("Username") is not None:
                new_data['Username'] = incoming_data.get('Username')

                with sqlite3.connect("QAT_Motors.db") as connect:
                    cursor = connect.cursor()
                    cursor.execute("UPDATE Admin SET Username =? WHERE Username=?", (new_data["Username"], username))
                    connect.commit()
                    response['Username'] = "Username Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("Password") is not None:
                new_data['Password'] = incoming_data.get('Password')

                with sqlite3.connect("QAT_Motors.db") as connect:
                    cursor = connect.cursor()
                    cursor.execute("UPDATE Admin SET Password =? WHERE Username=?", (new_data["Password"], username))
                    connect.commit()
                    response['Password'] = "Password Update was successful"
                    response['status_code'] = 200

    return response


if __name__ == '__main__':
    app.run()
