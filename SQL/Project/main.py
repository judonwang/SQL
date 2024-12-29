from configparser import ConfigParser
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from DATA225utils import make_connection
from matplotlib import pyplot as plt
import numpy as np

class MovieRatingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("mainwindow.ui",self)
        self.initUI()

    def initUI(self):

        self.topmoviesbutton = QPushButton('Top Movies', self)
        self.topmoviesbutton.clicked.connect(self.show_top_movies)

        self.newmoviesbutton = QPushButton('New Movies', self)
        self.newmoviesbutton.clicked.connect(self.show_new_movies)

        self.moviesbyruntimebutton = QPushButton('Movies by Runtime', self)
        self.moviesbyruntimebutton.clicked.connect(self.show_movies_by_runtime)

        self.moviesbygenrebutton = QPushButton('Movies by Genre', self)
        self.moviesbygenrebutton.clicked.connect(self.show_movies_by_genre)


        layout = QVBoxLayout()
        layout.addWidget(self.topmoviesbutton)
        layout.addWidget(self.newmoviesbutton)
        layout.addWidget(self.moviesbyruntimebutton)
        layout.addWidget(self.moviesbygenrebutton)
        

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(400, 400, 800, 600)
        self.setWindowTitle('Movie Analytics App')
        self.show()
       

    

    def read_config(self):
        config = ConfigParser()
        config.read('movie.ini')
        return config
    
    def query_database(self, sql_query):
        # Connect to the database using the configuration
        conn = make_connection(config_file='movie.ini')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result
    
    def display_result(self, result):
        # For demonstration, show the result in a label
        self.clear_central_widget()
        # Creating a table widget
        table = QTableWidget(self)
        table.setColumnCount(len(result[0]))
        table.setRowCount(len(result))
        table.setHorizontalHeaderLabels(["Budget", "Homepage", "id", "original_language", "Release_Date", "Revenue", "Runtime","Title"])

        # Populate the table with data
        for i, row in enumerate(result):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table.setItem(i, j, item)

        # Set table properties
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        # Set the table as the central widget
        self.setCentralWidget(table)

    def clear_central_widget(self):
        # Clear the central widget
        for i in reversed(range(self.centralWidget().layout().count())):
            self.centralWidget().layout().itemAt(i).widget().setParent(None)

    def show_top_movies(self):
        config = self.read_config()
        conn = make_connection(config_file='movie.ini')
        cursor = conn.cursor()

        # Display the analytics
        sql_query = """
        SELECT movies_metadata.release_date, movies_metadata.title, AVG(ratings.Rating) AS avg_rating
        FROM movies_metadata
        JOIN ratings ON movies_metadata.title = ratings.title
        GROUP BY movies_metadata.release_date, movies_metadata.title
        ORDER BY avg_rating DESC
        LIMIT 10
    """
        result = self.query_database(sql_query)

        # Visualization using Matplotlib - Histogram
        if result:
        # Extract data for plotting
            release_dates = [row[0] for row in result]
            movie_titles = [row[1] for row in result]
            avg_ratings = [row[2] for row in result]

            # Create a histogram using Matplotlib
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(movie_titles, avg_ratings, color='skyblue', edgecolor='black', alpha=0.7)

            # Set labels and title
            ax.set_xlabel('Movie Titles')
            ax.set_ylabel('Average Rating')
            ax.set_title('Top Movies Ratings Based on Release Date')

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')

            # Add data labels on top of the bars
            for bar, label in zip(bars, avg_ratings):
                height = bar.get_height()
                ax.annotate(f'{label:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

            plt.tight_layout()
            plt.show()

        conn.close()

    def show_new_movies(self):
        # Connect to the database and perform the query for new movies
        config = self.read_config()
        conn = make_connection(config_file='movie.ini')
        cursor = conn.cursor()
        # Display the analytics
        sql_query = "SELECT title, Release_Date FROM movies_metadata ORDER BY Release_Date  LIMIT 10"
        result = self.query_database(sql_query)
        self.display_result(result)

        # Visualization using Matplotlib
        titles = [row[0] for row in result]
        release_dates = [row[1] for row in result]

        plt.figure(figsize=(10, 6))
        plt.plot(titles, release_dates, marker='o', linestyle='-')
        plt.xlabel('Movie Titles')
        plt.ylabel('Release Date')
        plt.title('New Movies Based on Release Date')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Display the Matplotlib plot
        plt.show()

        # Close the database connection
        conn.close()


    def show_movies_by_runtime(self):
        # Connect to the database and perform the query for movies by runtime
        config = self.read_config()
        conn = make_connection(config_file='movie.ini')  
        cursor = conn.cursor()
        # Display the analytics
        sql_query = "SELECT title, runtime FROM movies_metadata ORDER BY runtime DESC LIMIT 10"
        result = self.query_database(sql_query)
        self.display_result(result)

        # Visualization using Matplotlib
        titles = [row[0] for row in result]
        runtimes = [row[1] for row in result]

        plt.figure(figsize=(10, 6))
        plt.scatter(titles, runtimes, color='green', marker='o')
        plt.xlabel('Movie Titles')
        plt.ylabel('Runtime (minutes)')
        plt.title('Top Movies Based on Runtime')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Display the Matplotlib plot
        plt.show()

        # Close the database connection
        conn.close()

        
    def show_movies_by_genre(self):
        # Connect to the database and perform the query for movies by genre
        # Display the analytics

        # For example, you can show the result in a label for demonstration
        self.show_result("Movies by Genre Analytics")

    def show_result(self, result):
        # For demonstration, show the result in a label
        result_label = QLabel(result, self)
        result_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(result_label)


if __name__ == '__main__':
    app = QApplication([])
    window = MovieRatingApp()
    app.exec_()


