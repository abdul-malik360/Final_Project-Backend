# Import modules needed
import sqlite3
import re

from flask import Flask, request
from flask_mail import Mail, Message


# putting all the tables in a class
class QatTables:
    def __init__(self):
        self.connect = sqlite3.connect('QAT_Motors.db')    # connecting sqlite3 to the database called QAT_Motors
        self.cursor = self.connect.cursor()

        # creating a table for admin    # command to create the table
        self.connect.execute("CREATE TABLE IF NOT EXISTS Admin(Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,"  
                             "Fullname TEXT NOT NULL,"   
                             "Username TEXT NOT NULL UNIQUE,"
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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'    # following code is used to send email's through flask
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '62545a@gmail.com'
app.config['MAIL_PASSWORD'] = 'zbuurwxtrtnotwvn'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)    # end of email code config


@app.route('/admin', methods=["POST", "GET"])   # created a route that has both get and post methods
def admin():    # function to add and show admin users
    response = {}   # making response an empty dictionary

    if request.method == "POST":    # if the function method is post admin registers data
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

    if request.method == "GET":    # if the function method is get, all data from the admin table is displayed
        response = {}

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM Admin")

            admin_users = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = admin_users
        return response


@app.route('/admin/<int:admin_id>', methods=["PUT", "GET"])   # created a route that has both put and get methods
def edit_admin(admin_id):
    response = {}

    if request.method == "PUT":     # this method will edit the admin user's data
        try:
            fullname = request.json['Fullname']
            username = request.json['Username']
            password = request.json['Password']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE Admin SET Fullname =?, Username=?, Password=? WHERE Admin_ID=?",
                               (fullname, username, password, admin_id))
                connect.commit()
                response['message'] = "Admin update was successful"
                response['status_code'] = 200

            return response

        except ValueError:
            response["message"] = "Admin update was unsuccessful, try again"
            response["status_code"] = 209
            return response

    if request.method == "GET":     # this method will delete the admin user
        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM Admin WHERE Admin_ID=" + str(admin_id))
            connect.commit()
            response['status_code'] = 204
            response['message'] = "Admin User deleted successfully"
        return response


@app.route('/client', methods=["POST", "GET"])      # a route for clients with post and get methods
def client():   # a function to add and view users
    response = {}

    if request.method == "POST":    # this method adds clients
        try:
            name = request.form['Name']
            surname = request.form['Surname']
            email = request.form['Email']
            cell = request.form['Cell']
            address = request.form['Address']
            username = request.form['Username']
            password = request.form['Password']

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'    # code to validate email entered

            # entry will only be accepted if email address and cell number is valid
            if re.search(regex, email):
                with sqlite3.connect("QAT_Motors.db") as connect:
                    cursor = connect.cursor()
                    cursor.execute("INSERT INTO Clients("
                                   "Name,"
                                   "Surname,"
                                   "Email,"
                                   "Cell,"
                                   "Address,"
                                   "Username,"
                                   "Password) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                   (name, surname, email, cell, address, username, password))
                    connect.commit()

                msg = Message('Welcome To QAT Motors', sender='62545a@gmail.com', recipients=[email])
                msg.body = "Thank you for registering to our services Mr " + surname
                mail.send(msg)

                response["message"] = "Success, Check Email"
                response["status_code"] = 201

            else:
                response['message'] = "Invalid Email Address"

        except ValueError:
            response['message'] = "Invalid Cell Number"

        return response


if __name__ == '__main__':
    app.run()
