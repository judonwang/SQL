import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from DATA225utils import make_connection

# I was thinking that I should keep the username after someone is logged in
# that way it would be easier to insert reviews and what not.
currentUser = ''

class mainWindow(QMainWindow):
    """
    The main stacked widget window. Consists of all other widgets and various buttons and functions
    """
    def __init__(self):
        super().__init__()

        # Creating stacked widget
        self.stacked = QStackedWidget(self)
        self.setCentralWidget(self.stacked)

        # Creating the widgets
        self.loginwid = LoginDialog()
        self.regwid = RegisterDialog()
        self.dataMenu = MenuDialog()
        self.ratingPage = RatingDialog()

        ######## Button Clicks #############

        # Creating the login widget
        self.loginwid.loginButton.clicked.connect(lambda: self.login(self.loginwid))    # finish log in code
        self.loginwid.registerButton.clicked.connect(lambda: self.switchLoginToRegister(self.regwid))
        self.stacked.addWidget(self.loginwid)

        # Creating the register page widget
        self.regwid.regButton.clicked.connect(lambda: self.register(self.regwid, 0))
        self.regwid.regBack.clicked.connect(lambda: self.switchToLogin(self.loginwid))
        self.stacked.addWidget(self.regwid)

        # Creating main menu widget
        self.dataMenu.reviewButton.clicked.connect(lambda: self.switchToRating())
        self.dataMenu.logoutButton.clicked.connect(lambda: self.switchToLogin(self.loginwid))
        self.stacked.addWidget(self.dataMenu)

        # Creating Rating Page
        self.ratingPage.ratingBack.clicked.connect(lambda: self.switchToMenu())
            # ...... finish this
    
    def switchLoginToRegister(self, regwid, index=1):
        """
        Switching pages from Login to Register
        Clears all boxes of text
        """
        self.stacked.setCurrentIndex(index)
        regwid.firstEntry.clear()
        regwid.lastEntry.clear()
        regwid.regnameEntry.clear()
        regwid.regpassEntry.clear()
        regwid.emailEntry.clear()
        regwid.confirmPass.clear()

    def switchToLogin(self, loginwid, index=0):
        """
        Switch pages from page to Login
        Clears boxes of text
        """
        self.stacked.setCurrentIndex(index)
        loginwid.usernameEntry.clear()
        loginwid.passwordEntry.clear()
        loginwid.loginError.setText('')

    
    def switchToMenu(self, index=2):
        """
        Switch pages to main menu
        """
        ### Currently main menu doesn't have any text (only buttons), so there is nothing to clear
        self.stacked.setCurrentIndex(index)
        self.dataMenu.label.setText(f'Welcome to the Movie Database, \n{currentUser}')
    
    def switchToRating(self, index=3):
        """
        Switch pages to rating page
        """
        self.stacked.setCurrentIndex(index)
        self.ratingPage.findMovie.clear()
        self.ratingPage.reviewSlide
        self.ratingPage.critiqueBox.clear()

    
    def login(self, loginwid):
        """
        Function for logging in
        Switches pages from login to main menu
        """

        ####### SQL Queries ###########
        conn = make_connection(config_file = 'proj_test.ini')
        cursor = conn.cursor()

        username = loginwid.usernameEntry.text()    # Getting user input for username and password
        password = loginwid.passwordEntry.text()


        # Query to get username and password pairs
        userpassQuery = ("""                             
                        SELECT u1.username, u2.password
                         FROM users u1, users u2
                         WHERE u1.username = u2.username
                        """)
        cursor.execute(userpassQuery)
        userPassPairs = cursor.fetchall()

        # Check if the user input pair is in our database
        if (username, password) not in userPassPairs:
            loginwid.loginError.setText('Wrong username or password')
        else:
            # Change the global var currentUser to the person who just logged in
            global currentUser
            currentUser = username
            self.switchToMenu()

            cursor.close()
            conn.close()


        cursor.close()
        conn.close()
    
    def register(self, regwid, index):
        """
        Function for registering an account
        """

        ####### SQL ###########
        conn = make_connection(config_file = 'proj_test.ini')
        cursor = conn.cursor()

        firstName = regwid.firstEntry.text()                      # entries in the gui text boxes
        lastName = regwid.lastEntry.text()
        username = regwid.regnameEntry.text()
        regpass = regwid.regpassEntry.text()
        email = regwid.emailEntry.text()
        confirmpass = regwid.confirmPass.text()
        gender = regwid.genderMenu.currentText()

        # Query to get the list of all usernames from our database
        userSQL = ("""SELECT username
                   FROM users
                   """)
        cursor.execute(userSQL)
        takenNames = [user[0] for user in cursor.fetchall()]     # list of existing usernames

        # Query to get the list of all emails from our database
        emailSQL = ("""SELECT email
                    FROM users
                    """)
        cursor.execute(emailSQL)
        takenMail = [mail[0] for mail in cursor.fetchall()]     # list of existing emails

        # Query to obtain a new user id for the new account
        idSQL = ("""SELECT max(user_id) + 1
                 FROM users""")
        cursor.execute(idSQL)
        userId = cursor.fetchall()[0][0]

        ######### Account Validation ###########

        if not firstName or not lastName or not username or not regpass or not confirmpass or not email:  
            regwid.errorLabel.setText('All fields are required')
        elif regpass != confirmpass:  
            regwid.errorLabel.setText('Passwords must match')
        elif username in takenNames:  
            regwid.errorLabel.setText('Username already exists')
        elif email in takenMail:
            regwid.errorLabel.setText('Email has already been used')
        else:
            # If we pass all the checks, insert this users information into the database and switch back to the log in screen

            userInsert = ("""
                        INSERT INTO users
                          """
                          f"VALUES ({userId}, '{firstName}', '{lastName}', '{username}', '{email}', '{regpass}', '{gender}')"
                          """
                        """)
            cursor.execute(userInsert)
            conn.commit()

            cursor.close()
            conn.close()
            self.switchToLogin(self.loginwid)


        cursor.close()
        conn.close()
    


class LoginDialog(QDialog):
    """
    Class for the Login Page
    Initializes the ui and hashes the password entry
    """
    def __init__(self):

        super().__init__()
        uic.loadUi('login_dialog.ui', self)
        self.passwordEntry.setEchoMode(QLineEdit.Password)

    

class RegisterDialog(QDialog):
    """
    Class for the register page
    Initializes the ui
    Hashes the password entries
    Creates a gender list
    """
    def __init__(self):

        super().__init__()
        uic.loadUi('register_dialog.ui', self)
        self.regpassEntry.setEchoMode(QLineEdit.Password)
        self.confirmPass.setEchoMode(QLineEdit.Password)
        for gen in ['Male', 'Female', 'Prefer not to say']:
            self.genderMenu.addItem(gen)

class MenuDialog(QDialog):
    """
    Initializes the menu ui
    """
    def __init__(self):

        super().__init__()
        uic.loadUi('mainMenu_dialog.ui', self)

class RatingDialog(QDialog):
    """
    Initializes the rating ui
    """
    def __init__(self):

        super().__init__()
        uic.loadUi('rating_dialog.ui', self)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mainWindow()
    window.setFixedWidth(600)   # Current height I have set it to.
    window.setFixedHeight(600)
    window.show()
    sys.exit(app.exec_())