# Import modules needed
import sqlite3
import re

from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from datetime import datetime
from flask_cors import CORS


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
                             "Title TEXT NOT NULL,"
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
                             "Day DATE NULL,"
                             "Time TIME NULL PRIMARY KEY,"
                             "CONSTRAINT fk_Vehicles FOREIGN KEY (Reg_Numb) REFERENCES Vehicles (Reg_Numb)"
                             "CONSTRAINT fk_Services FOREIGN KEY (Type) REFERENCES Services (Type))")
        print("Appointments table created successfully")
        self.connect.close()    # closes connection to database


QatTables()     # calling the class


def get_email(username):    # a function to retrieve email address of clients

    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT Email from Clients WHERE Username='" + str(username) + "'")
        return cursor.fetchone()


def get_username():    # a function to retrieve username of clients
    username = request.form['Username']

    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f"SELECT Username from Clients WHERE Username='{username}'")
        return cursor.fetchone()


def get_surname(username):    # a function to retrieve surname of clients

    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT Surname from Clients WHERE Username='" + str(username) + "'")
        return cursor.fetchone()


def get_title(username):    # a function to retrieve a title of clients

    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT Title from Clients WHERE Username='" + str(username) + "'")
        return cursor.fetchone()


# starting the Flask app
app = Flask(__name__)   # allows you to use api
CORS(app)
app.debug = True    # when finds a bug, it continues to run

app.config['MAIL_SERVER'] = 'smtp.gmail.com'    # following code is used to send email's through flask
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '62545a@gmail.com'
app.config['MAIL_PASSWORD'] = 'zbuurwxtrtnotwvn'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)    # end of email code config


@app.route('/client-login', methods=["PATCH"])
def client_login():
    response = {}
    username = request.json['Username']
    password = request.json['Password']

    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f"SELECT * from Clients WHERE Username='{username}' AND Password='{password}'")

        response['user'] = cursor.fetchone()
        response['message'] = "Details recovered"

        return response


@app.route('/admin-login', methods=["GET"])
def admin_login():
    response = {}
    username = request.json['Username']
    password = request.json['Password']

    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f"SELECT * from Admin WHERE Username='{username}' AND Password='{password}'")

        response['user'] = cursor.fetchone()
        response['message'] = "Details recovered"

        return response


@app.route('/admin', methods=["POST", "GET"])   # created a route that has both get and post methods
def admin():    # function to add and show admin users
    response = {}   # making response an empty dictionary

    if request.method == "POST":    # if the function method is post admin registers data
        fullname = request.json['Fullname']
        username = request.json['Username']
        password = request.json['Password']

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
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Admin")

            admin_users = cursor.fetchall()

            data = []

            for i in admin_users:
                data.append({u: i[u] for u in i.keys()})

        response['status_code'] = 200
        response['data'] = data
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
            name = request.json['Name']
            surname = request.json['Surname']
            title = request.json['Title']
            email = request.json['Email']
            cell = request.json['Cell']
            address = request.json['Address']
            username = request.json['Username']
            password = request.json['Password']

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'    # code to validate email entered

            # entry will only be accepted if email address is valid
            if re.search(regex, email):
                with sqlite3.connect("QAT_Motors.db") as connect:
                    cursor = connect.cursor()
                    cursor.execute("INSERT INTO Clients("
                                   "Name,"
                                   "Surname,"
                                   "Title,"
                                   "Email,"
                                   "Cell,"
                                   "Address,"
                                   "Username,"
                                   "Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                   (name, surname, title, email, cell, address, username, password))
                    connect.commit()

                msg = Message('Welcome To QAT Motors', sender='62545a@gmail.com', recipients=[email])
                msg.body = "Thank you for registering to our services " + title + " " + surname
                mail.send(msg)

                response["message"] = "Success, Check Email"
                response["status_code"] = 201

            else:
                response['message'] = "Invalid Email Address"

        except ValueError:
            response['message'] = "Invalid Cell Number"

        return response

    if request.method == "GET":    # if the function method is get, all data from the Client table is displayed
        response = {}

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Clients")

            client_users = cursor.fetchall()

            data = []

            for i in client_users:
                data.append({u: i[u] for u in i.keys()})

        response['status_code'] = 200
        response['data'] = data
        return jsonify(response)


@app.route('/client/<username>', methods=["PUT", "GET"])   # created a route that has both put and get methods
def edit_client(username):
    response = {}

    if request.method == "PUT":     # this method will edit the client's data
        try:
            name = request.json['Name']
            surname = request.json['Surname']
            title = request.json['Title']
            email = request.json['Email']
            cell = request.json['Cell']
            address = request.json['Address']
            # username = request.form['Username']
            password = request.json['Password']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE Clients SET Name=?, Surname=?, Title=?, Email=?, Cell=?, Address=?, Password=?"
                               " WHERE Username=?",
                               (name, surname, title, email, cell, address, password, username))
                connect.commit()
                response['message'] = "Client update was successful"
                response['status_code'] = 200

            return response

        except ValueError:
            response["message"] = "Client update was unsuccessful, try again"
            response["status_code"] = 209
            return response

    if request.method == "GET":     # this method will delete the client
        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM Clients WHERE Username='" + str(username) + "'")
            connect.commit()
            response['status_code'] = 204
            response['message'] = "Client deleted successfully"
        return response


# a route to view a client
@app.route('/view-client/<username>', methods=["GET"])
def view_client(username):
    response = {}
    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM Clients WHERE Username='" + str(username) + "'")
        response["status_code"] = 200
        response["message"] = "User retrieved successfully"
        response["data"] = cursor.fetchone()
    return jsonify(response)


@app.route('/vehicle', methods=["POST", "GET"])      # a route for vehicles with post and get methods
def vehicle():   # a function to add and view vehicles
    response = {}

    if request.method == "POST":    # this method adds vehicles
        try:
            car_type = request.json['Type']
            year_modal = request.json['Year_Modal']
            vin_numb = request.json['VIN_Numb']
            reg_numb = request.json['Reg_Numb']
            username = request.json['Username']

            email_tuple = get_email(username)
            email = ''.join(email_tuple)    # str.join() to convert tuple to string.
            print(email)

            title_tuple = get_title(username)
            title = ''.join(title_tuple)  # str.join() to convert tuple to string.
            print(title)

            surname_tuple = get_surname(username)
            surname = ''.join(surname_tuple)  # str.join() to convert tuple to string.
            print(surname)

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("INSERT INTO Vehicles("
                               "Type,"
                               "Year_Modal,"
                               "VIN_Numb,"
                               "Reg_Numb,"
                               "Username) VALUES(?, ?, ?, ?, ?)",
                               (car_type, year_modal, vin_numb, reg_numb, username))
                connect.commit()

                msg = Message('Vehicle Registration Successful', sender='62545a@gmail.com', recipients=[str(email)])
                msg.body = "Thank you for registering your vehicle to our services " + title + " " + surname
                mail.send(msg)

                response["message"] = "Successfully added vehicle, Check Email"
                response["status_code"] = 201

        except TypeError:      # check this
            response['message'] = "Invalid Username"

        return response

    if request.method == "GET":    # if the function method is get, all data from the Vehicles table is displayed
        response = {}

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Vehicles")

            vehicles = cursor.fetchall()

            data = []

            for i in vehicles:
                data.append({u: i[u] for u in i.keys()})

        response['status_code'] = 200
        response['data'] = data
        return jsonify(response)


@app.route('/vehicle/<reg_numb>', methods=["PUT", "GET"])   # created a route that has both put and get methods
def edit_vehicle(reg_numb):
    response = {}

    if request.method == "PUT":     # this method will edit the vehicle's data
        try:
            car_type = request.json['Type']
            year_modal = request.json['Year_Modal']
            vin_numb = request.json['VIN_Numb']
            # reg_numb = request.form['Reg_Numb']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE Vehicles SET Type=?, Year_Modal=?, VIN_Numb=?"
                               " WHERE Reg_Numb=?",
                               (car_type, year_modal, vin_numb, reg_numb))
                connect.commit()
                response['message'] = "Vehicle update was successful"
                response['status_code'] = 200

            return response

        except ValueError:
            response["message"] = "Vehicle update was unsuccessful, try again"
            response["status_code"] = 209
            return response

    if request.method == "GET":     # this method will delete the Vehicle
        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM Vehicles WHERE Reg_Numb='" + str(reg_numb) + "'")
            connect.commit()
            response['status_code'] = 204
            response['message'] = "Vehicle deleted successfully"
        return response


# a route to view a vehicle
@app.route('/view-vehicle/<reg_numb>', methods=["GET"])
def view_vehicle(reg_numb):
    response = {}
    with sqlite3.connect("QAT_Motors.db") as connect:
        cursor = connect.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Vehicles WHERE Reg_Numb='" + str(reg_numb) + "'")

        vehicle = cursor.fetchone()

        data = []

        for i in vehicle:
            data.append({u: i[u] for u in i})

    response['status_code'] = 200
    # response["message"] = "vehicle retrieved successfully"
    response['data'] = data

    return jsonify(response)


@app.route('/service', methods=["POST", "GET"])      # a route for services with post and get methods
def service():   # a function to add and view services
    response = {}

    if request.method == "POST":    # this method adds services
        try:
            service_type = request.json['Type']
            description = request.json['Description']
            duration = request.json['Duration']
            price = request.json['Price']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("INSERT INTO Services("
                               "Type,"
                               "Description,"
                               "Duration,"
                               "Price) VALUES(?, ?, ?, ?)",
                               (service_type, description, duration, price))
                connect.commit()

                response["message"] = "Successfully added service"
                response["status_code"] = 201

        except ValueError:
            response['message'] = "edit"

        return response

    if request.method == "GET":    # if the function method is get, all data from the Services table is displayed
        response = {}

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Services")

            services = cursor.fetchall()

            data = []

            for i in services:
                data.append({u: i[u] for u in i.keys()})

        response['status_code'] = 200
        response['data'] = data
        return response


@app.route('/service/<service_type>', methods=["PUT", "GET"])   # created a route that has both put and get methods
def edit_service(service_type):
    response = {}

    if request.method == "PUT":     # this method will edit the service's data
        try:
            # service_type = request.form['Type']
            description = request.json['Description']
            duration = request.json['Duration']
            price = request.json['Price']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE Services SET Description=?, Duration=?, Price=?"
                               " WHERE Type=?",
                               (description, duration, price, service_type))
                connect.commit()
                response['message'] = "Service update was successful"
                response['status_code'] = 200

            return response

        except ValueError:
            response["message"] = "Service update was unsuccessful, try again"
            response["status_code"] = 209
            return response

    if request.method == "GET":     # this method will delete the service
        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM Services WHERE Type='" + str(service_type) + "'")
            connect.commit()
            response['status_code'] = 204
            response['message'] = "Service deleted successfully"
        return response


@app.route('/appointments', methods=["POST", "GET"])      # a route for appointments with post and get methods
def appointments():   # a function to add and view appointments
    response = {}

    if request.method == "POST":    # this method adds appointments
        try:
            reg_numb = request.json['Reg_Numb']
            service_type = request.json['Type']
            day = request.json['Day']
            time = request.json['Time']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("INSERT INTO Appointments("
                               "Reg_Numb,"
                               "Type,"
                               "Day,"
                               "Time) VALUES(?, ?, ?, ?)",
                               (reg_numb, service_type, day, time))
                connect.commit()

                response["message"] = "Successfully added appointment"
                response["status_code"] = 201

        except ValueError:
            response['message'] = "edit"

        return response

    if request.method == "GET":    # if the function method is get, all data from the appointments table is displayed
        response = {}

        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Appointments")

            appointment = cursor.fetchall()

            data = []

            for i in appointment:
                data.append({u: i[u] for u in i.keys()})

        response['status_code'] = 200
        response['data'] = data
        return response


@app.route('/appointment/<reg_numb>', methods=["PUT", "GET"])   # created a route that has both put and get methods
def edit_appointment(reg_numb):
    response = {}

    if request.method == "PUT":     # this method will edit the appointment's data
        try:
            # reg_numb = request.form['Reg_Numb']
            service_type = request.json['Type']
            day = request.json['Day']
            time = request.json['Time']

            with sqlite3.connect("QAT_Motors.db") as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE Appointments SET Type=?, Day=?, Time=?"
                               " WHERE Reg_Numb=?",
                               (service_type, day, time, reg_numb))
                connect.commit()
                response['message'] = "Appointments update was successful"
                response['status_code'] = 200

            return response

        except ValueError:
            response["message"] = "Appointments update was unsuccessful, try again"
            response["status_code"] = 209
            return response

    if request.method == "GET":     # this method will delete the appointment's
        with sqlite3.connect("QAT_Motors.db") as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM Appointments WHERE Reg_Numb='" + str(reg_numb) + "'")
            connect.commit()
            response['status_code'] = 204
            response['message'] = "Appointment's deleted successfully"
        return response


if __name__ == '__main__':
    app.run()
