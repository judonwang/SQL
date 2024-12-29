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
        self.viewRating = ViewDialog()
        self.editPage = EditDialog()
        self.moviePage = MovieDialog()

        ######## Button Clicks #############

        # Creating the login widget
        self.loginwid.loginButton.clicked.connect(lambda: self.login())    # finish log in code
        self.loginwid.registerButton.clicked.connect(lambda: self.switchLoginToRegister())
        self.stacked.addWidget(self.loginwid)

        # Creating the register page widget
        self.regwid.regButton.clicked.connect(lambda: self.register())
        self.regwid.regBack.clicked.connect(lambda: self.switchToLogin())
        self.stacked.addWidget(self.regwid)

        # Creating main menu widget
        self.dataMenu.reviewButton.clicked.connect(lambda: self.switchToRating())
        self.dataMenu.logoutButton.clicked.connect(lambda: self.switchToLogin())
        self.dataMenu.allRates.clicked.connect(lambda: self.switchToView())
        self.dataMenu.findMovie.clicked.connect(lambda: self.switchToMovie())
        self.stacked.addWidget(self.dataMenu)

        # Creating Rating Page
        self.ratingPage.ratingSlider.valueChanged.connect(lambda: self.updateRating(self.ratingPage))
        self.ratingPage.ratingBack.clicked.connect(lambda: self.switchToMenu())
        self.ratingPage.submitReview.clicked.connect(lambda: self.review())
        self.stacked.addWidget(self.ratingPage)

        # Creating view ratings page
        self.viewRating.viewBack.clicked.connect(lambda: self.switchToMenu())
        self.viewRating.deleteButton.clicked.connect(lambda: self.deleteReview())
        self.stacked.addWidget(self.viewRating)

        # Creating edit ratings page
        self.editPage.editBack.clicked.connect(lambda: self.switchToView())
        self.editPage.editReview.clicked.connect(lambda: self.editReview())
        self.editPage.ratingSlider.valueChanged.connect(lambda: self.updateRating(self.editPage))
        self.stacked.addWidget(self.editPage)

        # Creating movie view page
        self.moviePage.movieBack.clicked.connect(lambda: self.switchToMenu())
        self.moviePage.submitButton.clicked.connect(lambda: self.findMovie())
        self.stacked.addWidget(self.moviePage)

    ############### Switching Pages ###################
    def switchToMovie(self, index=6):
        self.stacked.setCurrentIndex(index)
        self.moviePage.movieFind.clear()
        self.moviePage.reviewTable.clearContents()
        self.moviePage.reviewTable.setRowCount(0)
        self.moviePage.movieTitle.setText('')
        self.moviePage.ratingText.setText('')
        self.moviePage.numReview.setText('')
        self.moviePage.ratingTitle.setText('')
        self.moviePage.numTitle.setText('')
        self.moviePage.genreTitle.setText('')
        self.moviePage.genreLabel.setText('')

    
    def switchLoginToRegister(self, index=1):
        """
        Switching pages from Login to Register
        Clears all boxes of text
        """
        self.stacked.setCurrentIndex(index)
        self.regwid.firstEntry.clear()
        self.regwid.lastEntry.clear()
        self.regwid.regnameEntry.clear()
        self.regwid.regpassEntry.clear()
        self.regwid.emailEntry.clear()
        self.regwid.confirmPass.clear()
        self.regwid.errorLabel.setText('')

    def switchToLogin(self, index=0):
        """
        Switch pages from page to Login
        Clears boxes of text
        """
        self.stacked.setCurrentIndex(index)
        self.loginwid.usernameEntry.clear()
        self.loginwid.passwordEntry.clear()
        self.loginwid.loginError.setText('')
        global currentUser
        currentUser = ''

    
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
        self.ratingPage.ratingSlider.setValue(10)
        self.ratingPage.critiqueBox.clear()
        self.ratingPage.ratingError.setText('')
    
    def switchToView(self, index=4):
        """
        Switches pages to view
        Creates a table that has the following:
            Rows from a SQL query based on the current user
            A check box that allows the user to select what to delete
            An edit button to update that review
        """
        self.stacked.setCurrentIndex(index)
        self.viewRating.viewTable.clearContents()
        self.viewRating.delError.setText('')

        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()

        # SQL Query

        viewSQL = ("""
                    SELECT Rating_id, Rating, title, Critique, Date 
                   FROM ratings
                   """
                   f"WHERE Username = '{currentUser}'"
                   """
                   """)
        cursor.execute(viewSQL)
        allRatings = cursor.fetchall()

        # Initializing the table
        self.viewRating.viewTable.setRowCount(len(allRatings))

        for idx, ratings in enumerate(allRatings):
            editButton = QPushButton()    # Creating the edit button
            editButton.setText('Edit')
            chk_box = QTableWidgetItem(str(ratings[0]))   # Creating a checkbox that also shows the rating ID
            chk_box.setText(str(ratings[0]))
            chk_box.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_box.setCheckState(Qt.Unchecked)

            # Adding values into row idx at column 0-5
            self.viewRating.viewTable.setItem(idx, 0, chk_box)          
            self.viewRating.viewTable.setItem(idx, 1, QTableWidgetItem(str(ratings[1])))
            self.viewRating.viewTable.setItem(idx, 2, QTableWidgetItem(ratings[2]))
            self.viewRating.viewTable.setItem(idx, 3, QTableWidgetItem(ratings[3]))
            self.viewRating.viewTable.setItem(idx, 4, QTableWidgetItem(ratings[4]))
            self.viewRating.viewTable.setCellWidget(idx, 5, editButton)

            editButton.clicked.connect(lambda: self.switchToEdit(self.viewRating))  # Adding a function to the edit button
        
        cursor.close()
        conn.close()
    
    def switchToEdit(self, viewRating, index=5):
        """
        Switches to the edit page
        """
        # Obtains which row the edit click came from
        button = qApp.focusWidget()
        idx = viewRating.viewTable.indexAt(button.pos())

        # Clearing values; sets the rating ID and movie title..these cannot be changed
        self.stacked.setCurrentIndex(index)
        self.editPage.ratingSlider.setValue(10)
        self.editPage.editCritique.clear()
        self.editPage.ratingId.setText(viewRating.viewTable.item(idx.row(),0).text())
        self.editPage.editMovie.setText(viewRating.viewTable.item(idx.row(), 2).text())
    
    ############ Functions ###################

    def findMovie(self):
        """
        Update the movie information page
        Queries for a valid movie in the database
        Shows the title, genre, avg rating, number of reviews, critiques
        """
        selectedMovie = self.moviePage.movieFind.text()
        if not selectedMovie:
            self.moviePage.movieTitle.setText('Please enter a movie')
        else:
            conn = make_connection(config_file = 'operational.ini')
            cursor = conn.cursor()

            movieCheckQuery = ("""
                                SELECT title, genre
                                FROM movies
                               """
                               f"WHERE title = '{selectedMovie}'"
                               """
                                """)
            cursor.execute(movieCheckQuery)
            movieCheck = cursor.fetchall()

            movieQuery = ("""
                            SELECT AVG(Rating), COUNT(*)
                            FROM ratings r
                            """
                            f"WHERE title = '{selectedMovie}'"
                            """
                        """)
            cursor.execute(movieQuery)
            movieData = cursor.fetchall()[0]

            if not movieCheck:
                self.moviePage.movieTitle.setText("Sorry, we don't have that one")
                self.moviePage.reviewTable.clearContents()
                self.moviePage.reviewTable.setRowCount(0)
                self.moviePage.ratingText.setText('')
                self.moviePage.numReview.setText('')
                self.moviePage.ratingTitle.setText('')
                self.moviePage.numTitle.setText('')
                self.moviePage.genreTitle.setText('')
                self.moviePage.genreLabel.setText('')

            else:
                reviewQuery = ("""
                                SELECT Username, Rating, Critique
                                FROM ratings
                                """
                                f"WHERE title = '{selectedMovie}'"
                                """
                                """)
                cursor.execute(reviewQuery)
                reviewData = cursor.fetchall()

                self.moviePage.movieTitle.setText(selectedMovie)
                self.moviePage.ratingTitle.setText('Average Rating:')
                self.moviePage.ratingText.setText(f"{movieData[0]}/10")
                self.moviePage.numTitle.setText('# Reviews:')
                self.moviePage.numReview.setText(str(movieData[1]))
                self.moviePage.genreTitle.setText('Genre: ')
                self.moviePage.genreLabel.setText(movieCheck[0][1])

                self.moviePage.reviewTable.setRowCount(len(reviewData))

                for idx, review in enumerate(reviewData):
                    self.moviePage.reviewTable.setItem(idx, 0, QTableWidgetItem(review[0]))
                    self.moviePage.reviewTable.setItem(idx, 1, QTableWidgetItem(str(review[1])))
                    self.moviePage.reviewTable.setItem(idx, 2, QTableWidgetItem(review[2]))

            
            cursor.close()
            conn.close()

    
    def editReview(self):
        """
        Edit Review Function
        Obtains user values
        Makes SQL UPDATE query based on those values
        """
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()
        
        # User input values
        ratingID = self.editPage.ratingId.text()
        rateNum = self.editPage.ratingSlider.value()/10
        critique = self.editPage.editCritique.toPlainText()

        ############ SQL ###############
        dateSQL = ("""SELECT CURRENT_DATE()""")
        cursor.execute(dateSQL)
        getDate = cursor.fetchall()[0][0]

        # Updates the row
        updateSQL = ("""
                    UPDATE ratings
                    """
                    f"SET Rating = {rateNum}, Critique = '{critique}', Date = '{getDate}'"
                    f"WHERE Rating_id = {ratingID}"
                    """
                    """)
        
        cursor.execute(updateSQL)
        conn.commit()

        cursor.close()
        conn.close()

        self.switchToView()

    
    def deleteReview(self):
        """
        Delete review function
        Checks which checkboxes have been selected; if none are selected, changes error message
        If there are checkboxes selected, deletes the review with that row's rating ID
        """
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()     

        # Obtains every rating ID that was selected
        select_list = []
        for i in range(self.viewRating.viewTable.rowCount()):
            if self.viewRating.viewTable.item(i, 0).checkState():
                select_list.append(int(self.viewRating.viewTable.item(i,0).text()))
        
        # Checks if there are any selected entries before making any queries
        if not select_list:
            self.viewRating.delError.setText('Select a movie(s) to delete with the checkboxes')
        else:
            # SQL uses tuples, so we convert the list (there's probably a better way to do this)
            if len(select_list) > 1:
                sel_del = tuple(select_list)
            else:
                sel_del = f"({select_list[0]})"

            # Delete from db
            delSQL = ("""
                        DELETE FROM ratings
                    """
                    f"WHERE Rating_id IN {sel_del}"
                    """
                    """)
            cursor.execute(delSQL)
            conn.commit()

            cursor.close()
            conn.close()

            # Refresh the page
            self.switchToView()

 
    def login(self):
        """
        Function for logging in
        Switches pages from login to main menu
        """

        ####### SQL Queries ###########
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()

        username = self.loginwid.usernameEntry.text()    # Getting user input for username and password
        password = self.loginwid.passwordEntry.text()


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
            self.loginwid.loginError.setText('Wrong username or password')
        else:
            # Change the global var currentUser to the person who just logged in
            global currentUser
            currentUser = username
            self.switchToMenu()

            cursor.close()
            conn.close()


        cursor.close()
        conn.close()
    
    def register(self):
        """
        Function for registering an account
        """

        ####### SQL ###########
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()

        firstName = self.regwid.firstEntry.text()                # entries in the gui text boxes
        lastName = self.regwid.lastEntry.text()
        username = self.regwid.regnameEntry.text()
        regpass = self.regwid.regpassEntry.text()
        email = self.regwid.emailEntry.text()
        confirmpass = self.regwid.confirmPass.text()
        gender = self.regwid.genderMenu.currentText()

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
            self.regwid.errorLabel.setText('All fields are required')
        elif regpass != confirmpass:  
            self.regwid.errorLabel.setText('Passwords must match')
        elif username in takenNames:  
            self.regwid.errorLabel.setText('Username already exists')
        elif email in takenMail:
            self.regwid.errorLabel.setText('Email has already been used')
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
            self.switchToLogin()


        cursor.close()
        conn.close()
    
    def updateRating(self, page):
        """
        Updates the rating slider text box for the rating page and edit rating page
        """
        value = page.ratingSlider.value()
        page.ratingLabel.setText(f'{value/10}/10')

    
    def review(self):
        """
        Function for entering a review on the review page
        """
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()
        
        # User input values
        selectedMovie = self.ratingPage.findMovie.text()
        rateNum = self.ratingPage.ratingSlider.value()/10
        critique = self.ratingPage.critiqueBox.toPlainText()


        # Obtain a new, unique rating id
        idSQL = ("""SELECT max(Rating_id) + 1
            FROM ratings""")
        cursor.execute(idSQL)
        ratingId = cursor.fetchall()[0][0]

        # Gets the current date
        dateSQL = ("""SELECT CURRENT_DATE()""")
        cursor.execute(dateSQL)
        getDate = cursor.fetchall()[0][0]

        # If the user did not enter a movie, give error
        if not selectedMovie:
            self.ratingPage.ratingError.setText('You must select a movie to rate')
        else:
            # Try/except: If the user input a movie that does not exist in the db
            try:
                # Queries for the movie; if in db, inserts their rating
                movieSQL = ("""
                        SELECT id
                    FROM movies
                    """
                    f"WHERE title='{selectedMovie}'"
                    """
                    """)
                cursor.execute(movieSQL)
                movieId = cursor.fetchall()[0][0]


                reviewInsert = ("""
                                INSERT INTO ratings
                                """
                                f"VALUES({ratingId}, {rateNum}, {movieId}, '{selectedMovie}', '{currentUser}', '{critique}', '{getDate}')"
                                """
                                """)
                cursor.execute(reviewInsert)
                conn.commit()
                cursor.close()
                conn.close()
                self.switchToRating()
            except:
                # If the query returned nothing, set error
                self.ratingPage.ratingError.setText("We don't have that movie.")


        cursor.close()
        conn.close()
        # Should I make it go back to the previous page, or stay on the same page so they can keep adding in reviews...
    


class LoginDialog(QDialog):
    """
    Class for the Login Page
    Initializes the ui and hashes the password entry
    """
    def __init__(self):

        super().__init__()
        uic.loadUi('login_dialog.ui', self)
        self.loginError.setText('')
        self.passwordEntry.setEchoMode(QLineEdit.Password)  # Hiding password

    

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
        self.regpassEntry.setEchoMode(QLineEdit.Password)   # Hiding password
        self.confirmPass.setEchoMode(QLineEdit.Password)
        for gen in ['Male', 'Female', 'Prefer not to say']: # Creating gender list (can add more)
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
        self.ratingError.setText('')
        self.ratingSlider.setValue(10)   
        self.ratingLabel.setText('1.0/10')

        # Creating autocomplete based on movies in our db
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()
        # Queries for all movie titles in db
        movieTitleSQL = ("""
                        SELECT title
                         FROM movies
                         """)
        cursor.execute(movieTitleSQL)
        movieList = [title[0] for title in cursor.fetchall()] 
        # Create QCompleter object with the movies we queried for
        completer = QCompleter(movieList)
        completer.setMaxVisibleItems(5)  # Shows 5 max so it doesn't take too much space
        completer.setCaseSensitivity(Qt.CaseInsensitive)  # Makes it case insensitive
        self.findMovie.setCompleter(completer)

        cursor.close()
        conn.close()

class ViewDialog(QDialog):
    """
    Initializes the view rating page
    """
    def __init__(self):

        super().__init__()
        uic.loadUi('view_dialog.ui', self)
        # Initializing the table to hold our queries
        labels = ['Rating_id', 'Rating', 'title', 'Critique', 'Date', 'Edit?'] # Column names
        self.viewTable.setColumnCount(6)  # Total columns in table
        self.viewTable.setHorizontalHeaderLabels(labels)  # Renaming columns

class EditDialog(QDialog):
    """
    Initializes the edit rating page
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('edit_dialog.ui', self)
        self.ratingSlider.setValue(10)
        self.ratingLabel.setText('1.0/10')


class MovieDialog(QDialog):
    """
    Initializes the movie find page
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('movie_dialog.ui', self)
         # Creating autocomplete based on movies in our db
        conn = make_connection(config_file = 'operational.ini')
        cursor = conn.cursor()
        # Queries for all movie titles in db
        movieTitleSQL = ("""
                        SELECT title
                         FROM movies
                         """)
        cursor.execute(movieTitleSQL)
        movieList = [title[0] for title in cursor.fetchall()] 
        # Create QCompleter object with the movies we queried for
        completer = QCompleter(movieList)
        completer.setMaxVisibleItems(5)  # Shows 5 max so it doesn't take too much space
        completer.setCaseSensitivity(Qt.CaseInsensitive)  # Makes it case insensitive
        self.movieFind.setCompleter(completer)

        cursor.close()
        conn.close()

        labels = ['Username', 'Rating', 'Critique']
        self.reviewTable.setColumnCount(3)
        self.reviewTable.setHorizontalHeaderLabels(labels)
        self.reviewTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.reviewTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.reviewTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mainWindow()
    window.setFixedWidth(900)   # Current height I have set it to.
    window.setFixedHeight(800)
    window.show()
    sys.exit(app.exec_())