import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QWidget
import mysql.connector
import matplotlib.pyplot as plt
from configparser import ConfigParser
from DATA225utils import make_connection

class AnalyticalDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Movie Analytics Dashboard")
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.init_ui()

    def init_ui(self):
        # Create a layout for the movie selection section
        movie_selection_layout = QHBoxLayout()

        # Create dropdowns for selecting two movies
        self.movie_selector_label_1 = QLabel("Select Movie 1:")
        self.movie_selector_1 = QComboBox()

        self.movie_selector_label_2 = QLabel("Select Movie 2:")
        self.movie_selector_2 = QComboBox()

        # Connect the movie selections to a function
        self.movie_selector_1.currentIndexChanged.connect(self.update_movie_selection)
        self.movie_selector_2.currentIndexChanged.connect(self.update_movie_selection)

        # Add widgets to the movie selection layout
        movie_selection_layout.addWidget(self.movie_selector_label_1)
        movie_selection_layout.addWidget(self.movie_selector_1)
        movie_selection_layout.addWidget(self.movie_selector_label_2)
        movie_selection_layout.addWidget(self.movie_selector_2)

        # Add the movie selection layout to the main layout
        self.layout.addLayout(movie_selection_layout)

        # Create buttons for different analytics
        self.button_ratings = QPushButton("Compare Ratings")
        self.button_revenue = QPushButton("Compare Revenue")
        self.button_runtime = QPushButton("Compare Runtime")

        # Connect buttons to corresponding functions
        self.button_ratings.clicked.connect(self.show_ratings_comparison)
        self.button_revenue.clicked.connect(self.show_revenue_comparison)
        self.button_runtime.clicked.connect(self.show_runtime_comparison)

        # Add buttons to the main layout
        self.layout.addWidget(self.button_ratings)
        self.layout.addWidget(self.button_revenue)
        self.layout.addWidget(self.button_runtime)

        self.central_widget.setLayout(self.layout)

        # Populate movie dropdowns with data from the database
        self.populate_movie_dropdowns()

    def show_ratings_comparison(self):
        movie1 = self.movie_selector_1.currentText()
        movie2 = self.movie_selector_2.currentText()

        # Fetch ratings data from the database (replace with your actual logic)
        ratings_movie1 = self.fetch_ratings_from_database(movie1)
        ratings_movie2 = self.fetch_ratings_from_database(movie2)

        # Check if ratings are None
        if ratings_movie1 is None or ratings_movie2 is None:
            print("No ratings data available.")
            return

        # Aggregate the ratings (e.g., take the mean)
        average_ratings = [sum(ratings_movie1) / len(ratings_movie1), sum(ratings_movie2) / len(ratings_movie2)]

        # Create a bar chart for ratings
        labels = [movie1, movie2]
        plt.bar(labels, average_ratings, color=['blue', 'green'])
        plt.xlabel('Movies')
        plt.ylabel('Average Ratings')
        plt.title('Ratings Comparison')
        plt.show()

    def fetch_ratings_from_database(self, movie_name):
        # Fetch ratings data from the database (replace with your actual logic)
        db_config = {
            'host': 'IES-ADS-ClassDB.sjsu.edu',
            'user': 'bytes_user',
            'password': 'Apricot_859',
            'database': 'bytes_db'
        }

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute a query to fetch ratings for the selected movie
        cursor.execute(f"SELECT rating FROM ratings WHERE title = '{movie_name}'")
        
        # Fetch all results
        results = cursor.fetchall()

        # Check if there are results
        if results:
            # Assuming you want to fetch ratings for all rows
            ratings = [result[0] for result in results]
        else:
            ratings = None  # Handle the case where no result is found

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return ratings


    def show_revenue_comparison(self):
        movie1 = self.movie_selector_1.currentText()
        movie2 = self.movie_selector_2.currentText()

        # Fetch revenue data from the database (replace with your actual logic)
        revenue_movie1 = self.fetch_revenue_from_database(movie1)
        revenue_movie2 = self.fetch_revenue_from_database(movie2)

        # Create a bar chart for revenue
        labels = [movie1, movie2]
        revenue_data = [revenue_movie1, revenue_movie2]

        plt.bar(labels, revenue_data, color=['blue', 'green'])
        plt.xlabel('Movies')
        plt.ylabel('Revenue in billions')
        plt.title('Revenue Comparison')
        plt.show()

    def fetch_revenue_from_database(self, movie_name):
         # Fetch revenue data from the database (replace with your actual logic)
        db_config = {
            'host': 'IES-ADS-ClassDB.sjsu.edu',
            'user': 'bytes_user',
            'password': 'Apricot_859',
            'database': 'bytes_db'
            }

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

            # Execute a query to fetch revenue for the selected movie
        cursor.execute(f"SELECT revenue FROM movies WHERE title = '{movie_name}'")
        revenue = cursor.fetchone()[0]  # Assuming revenue is a column in your database

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return revenue



    def show_runtime_comparison(self):
        movie1 = self.movie_selector_1.currentText()
        movie2 = self.movie_selector_2.currentText()

        # Fetch runtime data from the database (replace with your actual logic)
        runtime_movie1 = self.fetch_runtime_from_database(movie1)
        runtime_movie2 = self.fetch_runtime_from_database(movie2)

        # Create a bar chart for runtime comparison
        labels = [movie1, movie2]
        runtime_data = [runtime_movie1, runtime_movie2]

        plt.bar(labels, runtime_data, color=['orange', 'purple'])
        plt.xlabel('Movies')
        plt.ylabel('Runtime (minutes)')
        plt.title('Runtime Comparison')
        plt.show()

    def fetch_runtime_from_database(self, movie_name):
        # Fetch runtime data from the database (replace with your actual logic)
        db_config = {
            'host': 'IES-ADS-ClassDB.sjsu.edu',
            'user': 'bytes_user',
            'password': 'Apricot_859',
            'database': 'bytes_db'
        }

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute a query to fetch runtime for the selected movie
        cursor.execute(f"SELECT runtime FROM movies WHERE title = '{movie_name}'")
        runtime = cursor.fetchone()[0]  # Assuming runtime is a column in your database

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return runtime


    def update_movie_selection(self, index):
        selected_movie_1 = self.movie_selector_1.currentText()
        selected_movie_2 = self.movie_selector_2.currentText()
        print(f"Selected Movies: {selected_movie_1}, {selected_movie_2}")

    def fetch_movies_from_database(self):
        # Replace the following with your actual database connection details
        db_config = {
            'host': 'IES-ADS-ClassDB.sjsu.edu',
            'user': 'bytes_user',
            'password': 'Apricot_859',
            'database': 'bytes_wh'
        }

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute a query to fetch movies from the database
        cursor.execute("SELECT title FROM movies_metadata")
        movies_from_db = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return movies_from_db

    def populate_movie_dropdowns(self):
        # Fetch movies from the database and populate dropdowns
        movies = self.fetch_movies_from_database()
        self.movie_selector_1.addItems(movies)
        self.movie_selector_2.addItems(movies)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = AnalyticalDashboard()
    dashboard.show()
    sys.exit(app.exec_())
