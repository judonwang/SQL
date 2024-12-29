import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QComboBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import mysql.connector
from configparser import ConfigParser

class GenreVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Genre Visualization Dashboard")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Create buttons for different visualizations
        self.button_genre_count = QPushButton("Number of Movies per Genre")
        self.button_avg_rating = QPushButton("Average Movie Rating per Genre")
        self.button_avg_rating_per_year = QPushButton("Average Rating Per Genre Each Year")

        # Create a QHBoxLayout for genre selection components
        genre_selection_layout = QHBoxLayout()

        # Create QLabel and QComboBox for genre selection
        self.genre_selector_label = QLabel("Select Genre:")
        self.genre_selector = QComboBox()

        # Add QLabel and QComboBox to the genre_selection_layout
        genre_selection_layout.addWidget(self.genre_selector_label)
        genre_selection_layout.addWidget(self.genre_selector)

        # Connect buttons to corresponding functions
        self.button_genre_count.clicked.connect(self.show_genre_count_visualization)
        self.button_avg_rating.clicked.connect(self.show_avg_rating_visualization)
        self.button_avg_rating_per_year.clicked.connect(self.show_avg_rating_per_year_line_chart_visualization)

        # Add buttons and genre_selection_layout to the main layout
        self.layout.addWidget(self.button_genre_count)
        self.layout.addWidget(self.button_avg_rating)
        self.layout.addWidget(self.button_avg_rating_per_year)
        self.layout.addLayout(genre_selection_layout)

        self.central_widget.setLayout(self.layout)

        # Load database connection details from .ini file
        self.db_config = self.load_db_config_from_ini()

        # Populate the genre dropdown
        self.populate_genre_dropdown()

    def load_db_config_from_ini(self):
        config = ConfigParser()
        config.read('movie.ini')  
        return {
            'localhost': config['mysql']['host'],
            'root': config['mysql']['user'],
            'root': config['mysql']['password'],
            'movie': config['mysql']['database'],
        }

    def fetch_data_from_database(self, query):
        connection = mysql.connector.connect(
        host=self.db_config['localhost'],
        user=self.db_config['root'],
        password=self.db_config['root'],
        database=self.db_config['movie']
    )
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()
        connection.close()

        return data

    def show_genre_count_visualization(self):
        query = "SELECT genre, COUNT(*) as count FROM movies_metadata GROUP BY genre"
        data = self.fetch_data_from_database(query)

        labels = [item['genre'] for item in data]
        counts = [item['count'] for item in data]

        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Percentage of Movies per Genre')
        plt.show()

    def show_avg_rating_visualization(self):
        query = "SELECT genre, AVG(rating) as avg_rating FROM ratings, movies_metadata GROUP BY genre"
        data = self.fetch_data_from_database(query)

        labels = [item['genre'] for item in data]
        avg_ratings = [item['avg_rating'] for item in data]

        plt.pie(avg_ratings, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        plt.title('Percentage of Average Movie Rating per Genre')
        plt.show()

    def populate_genre_dropdown(self):
        # Fetch genres from the database and populate the dropdown
        query = "SELECT DISTINCT genre FROM movies_metadata"
        data = self.fetch_data_from_database(query)
        genres = [item['genre'] for item in data]
        self.genre_selector.addItems(genres)

    def show_avg_rating_per_year_line_chart_visualization(self):
        selected_genre = self.genre_selector.currentText()

        # SQL query to fetch data for the selected genre
        query = f"""
            SELECT AVG(rating) as avg_rating, YEAR(release_date) as release_year
            FROM ratings JOIN movies_metadata ON ratings.title = movies_metadata.title
            WHERE movies_metadata.genre = '{selected_genre}'
            GROUP BY release_year
        """
        data = self.fetch_data_from_database(query)

        if not data:
            print(f"No data available for {selected_genre}")
            return

        # Separate the data into 'release_year' and 'avg_rating'
        release_years = [item['release_year'] for item in data]
        avg_ratings = [item['avg_rating'] for item in data]

        # Plot the line chart
        plt.figure(figsize=(10, 6))
        plt.plot(release_years, avg_ratings, marker='o', linestyle='-')
        plt.xlabel('Release Year')
        plt.ylabel('Average Rating')
        plt.title(f'Average Ratings for {selected_genre} Genre Over Years')
        plt.xticks(rotation=90, fontsize=8)
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    genre_app = GenreVisualizationApp()
    genre_app.show()
    sys.exit(app.exec_())
