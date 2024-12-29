import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QComboBox, QFormLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import mysql.connector
from configparser import ConfigParser
from datetime import datetime
import pandas as pd


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
        self.button_drill_down_date = QPushButton("Drill Down on Date")

        # Create a QHBoxLayout for genre selection components
        genre_selection_layout_1 = QHBoxLayout()
        genre_selection_layout_2 = QHBoxLayout()

        # Create QLabel and QComboBox for genre selection
        self.genre_selector_label_1 = QLabel("Select Genre 1:")
        self.genre_selector = QComboBox()
        self.genre_selector_label_2 = QLabel("Select Genre 2:")
        self.genre_selector_2 = QComboBox()

        # Add QLabel and QComboBox to the genre_selection_layout
        genre_selection_layout_1.addWidget(self.genre_selector_label_1)
        genre_selection_layout_1.addWidget(self.genre_selector)
        genre_selection_layout_2.addWidget(self.genre_selector_label_2)
        genre_selection_layout_2.addWidget(self.genre_selector_2)

        # Connect buttons to corresponding functions
        self.button_genre_count.clicked.connect(self.show_genre_count_visualization)
        self.button_avg_rating.clicked.connect(self.show_avg_rating_visualization)
        self.button_avg_rating_per_year.clicked.connect(self.show_avg_rating_per_year_line_chart_visualization)
        self.button_drill_down_date.clicked.connect(self.show_drill_down_options)  # Change to show drill-down options

        # Add buttons and genre_selection_layout to the main layout
        self.layout.addWidget(self.button_genre_count)
        self.layout.addWidget(self.button_avg_rating)
        self.layout.addWidget(self.button_avg_rating_per_year)
        self.layout.addLayout(genre_selection_layout_1)
        self.layout.addLayout(genre_selection_layout_2)
        

        # Add widgets for drill-down options (initially hidden)
        self.drill_down_layout = QFormLayout()
        self.granularity_selector = QComboBox()
        self.granularity_selector.addItem("Year")
        self.granularity_selector.addItem("Month")
        self.granularity_selector.addItem("Day")
        self.drill_down_layout.addRow("Granularity:", self.granularity_selector)
        self.button_ok = QPushButton("Drill Down To Date")
        self.button_ok.clicked.connect(self.handle_drill_down_ok)
        self.drill_down_layout.addRow(self.button_ok)

        # Initially hide the drill-down widgets
        self.drill_down_layout.setEnabled(False)

        # Add the drill-down widgets to the main layout
        self.layout.addLayout(self.drill_down_layout)

        self.central_widget.setLayout(self.layout)

        # Load database connection details from .ini file
        self.db_config = self.load_db_config_from_ini()

        # Populate the genre dropdown
        self.populate_genre_dropdown_1()
        self.populate_genre_dropdown_2()

    def load_db_config_from_ini(self):
        config = ConfigParser()
        config.read('movie.ini')
        return {
            'IES-ADS-ClassDB.sjsu.edu': config['mysql']['host'],
            'bytes_user': config['mysql']['user'],
            'Apricot_859': config['mysql']['password'],
            'bytes_wh': config['mysql']['database'],
        }

    def fetch_data_from_database(self, query):
        connection = mysql.connector.connect(
            host=self.db_config['IES-ADS-ClassDB.sjsu.edu'],
            user=self.db_config['bytes_user'],
            password=self.db_config['Apricot_859'],
            database=self.db_config['bytes_wh']
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

        # Create a bar chart for genre count visualization
        plt.bar(labels, counts, color=plt.cm.Paired.colors)
        plt.xlabel('Genre')
        plt.ylabel('Number of Movies')
        plt.title('Number of Movies per Genre')
        plt.xticks(rotation=45, ha='right')
        plt.show()

    def show_avg_rating_visualization(self):
        query1 = """SELECT genre, AVG(rating) as avg_rating FROM rating, movies_metadata 
                    where rating.title=movies_metadata.title
                    GROUP BY genre"""
        data = self.fetch_data_from_database(query1)

        labels = [item['genre'] for item in data]
        avg_ratings = [item['avg_rating'] for item in data]

        # Create a bar chart for average rating visualization
        plt.bar(labels, avg_ratings, color=plt.cm.Paired.colors)
        plt.xlabel('Genre')
        plt.ylabel('Average Rating')
        plt.title('Average Movie Rating per Genre')
        plt.xticks(rotation=45, ha='right')
        plt.show()

    def populate_genre_dropdown_1(self):
        # Fetch genres from the database and populate the dropdown
        query = "SELECT DISTINCT genre FROM movies_metadata"
        data = self.fetch_data_from_database(query)
        genres = [item['genre'] for item in data]
        self.genre_selector.addItems(genres)

    def populate_genre_dropdown_2(self):
        # Fetch genres from the database and populate the second dropdown
        query = "SELECT DISTINCT genre FROM movies_metadata"
        data = self.fetch_data_from_database(query)
        genres = [item['genre'] for item in data]
        self.genre_selector_2.addItems(genres)

    def show_avg_rating_per_year_line_chart_visualization(self):
        selected_genre_1 = self.genre_selector.currentText()
        selected_genre_2 = self.genre_selector_2.currentText()
        granularity = self.granularity_selector.currentText()

        # Define date_select_clause and group_by_clause based on granularity
        if granularity == "Year":
            group_by_clause = "GROUP BY Year(Date)"
            order_by_clause = "ORDER BY Year(Date)"
            date_select_clause = "Year(Date) as release_year"
            x_label_format = "%Y"
        elif granularity == "Month":
            group_by_clause = "GROUP BY Year(Date), Month(Date)"
            order_by_clause = "ORDER BY Year(Date), Month(Date)"
            date_select_clause = "Year(Date) as release_year, Month(Date) as release_month"
            x_label_format = "%b %Y"
        elif granularity == "Day":
            group_by_clause = "GROUP BY Year(Date), Month(Date), Day(Date)"
            order_by_clause = "ORDER BY Year(Date), Month(Date), Day(Date)"
            date_select_clause = "Year(Date) as release_year, Month(Date) as release_month, Day(Date) as release_day"
            x_label_format = "%d %b %Y"
        else:
            print("Invalid granularity selected")
            return

        # Fetch data for the first selected genre
        query_1 = f"""
            SELECT AVG(rating) as avg_rating, {date_select_clause}
            FROM rating JOIN movies_metadata ON rating.title = movies_metadata.title
            WHERE movies_metadata.genre = '{selected_genre_1}'
            {group_by_clause}
            {order_by_clause}
        """
        data_1 = self.fetch_data_from_database(query_1)

        # Fetch data for the second selected genre
        query_2 = f"""
            SELECT AVG(rating) as avg_rating, {date_select_clause}
            FROM rating JOIN movies_metadata ON rating.title = movies_metadata.title
            WHERE movies_metadata.genre = '{selected_genre_2}'
            {group_by_clause}
            {order_by_clause}
        """
        data_2 = self.fetch_data_from_database(query_2)

        # Combine the date components for proper x-axis labels
        if granularity == "Year":
            release_dates_1 = [item['release_year'] for item in data_1]
            release_dates_2 = [item['release_year'] for item in data_2]
        elif granularity == "Month":
            release_dates_1 = [datetime(item['release_year'], item['release_month'], 1) for item in data_1]
            release_dates_2 = [datetime(item['release_year'], item['release_month'], 1) for item in data_2]
        elif granularity == "Day":
            release_dates_1 = [datetime(item['release_year'], item['release_month'], item['release_day']) for item in data_1]
            release_dates_2 = [datetime(item['release_year'], item['release_month'], item['release_day']) for item in data_2]

        # Create DataFrames for easier sorting
        df_1 = pd.DataFrame({'Date': release_dates_1, 'Average Rating': [item['avg_rating'] for item in data_1]})
        df_2 = pd.DataFrame({'Date': release_dates_2, 'Average Rating': [item['avg_rating'] for item in data_2]})

        # Sort DataFrames by date
        df_1 = df_1.sort_values(by='Date')
        df_2 = df_2.sort_values(by='Date')

        # Check if the user selected two different genres
        if selected_genre_1 != selected_genre_2:
            # Create subplots
            fig, axs = plt.subplots(2, 1, figsize=(10, 12), sharex=True)
            axs[0].plot(df_1['Date'], df_1['Average Rating'], label=f'{selected_genre_1}', marker='o', linestyle='-', color='blue')
            axs[1].plot(df_2['Date'], df_2['Average Rating'], label=f'{selected_genre_2}', marker='o', linestyle='-', color='orange')

            axs[0].set_ylabel('Average Rating')
            axs[0].set_title(f'Average Ratings for {selected_genre_1} Genre Over Dates')
            axs[1].set_xlabel('Release Date')
            axs[1].set_ylabel('Average Rating')
            axs[1].set_title(f'Average Ratings for {selected_genre_2} Genre Over Dates')

        else:
            # Plot on a single graph if the genres are the same
            plt.figure(figsize=(10, 6))
            plt.plot(df_1['Date'], df_1['Average Rating'], label=f'{selected_genre_1}', marker='o', linestyle='-', color='blue')
            plt.plot(df_2['Date'], df_2['Average Rating'], label=f'{selected_genre_2}', marker='o', linestyle='-', color='orange')

            plt.xlabel('Release Date')
            plt.ylabel('Average Rating')
            plt.title(f'Average Ratings for {selected_genre_1} and {selected_genre_2} Genres Over Dates')
            plt.xticks(rotation=45, fontsize=8, ha='right')
            plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(x_label_format))
            plt.legend()  # Display legend to differentiate between genres
            plt.grid(True)

        plt.show()

    def show_drill_down_options(self):
        # Toggle the visibility of the drill-down options
        self.drill_down_layout.setEnabled(not self.drill_down_layout.isEnabled())

    def handle_drill_down_ok(self):
        # Handle the OK button click for drill-down
        selected_granularity = self.granularity_selector.currentText()
        self.show_avg_rating_per_year_line_chart_visualization()
        print(f"Selected Granularity: {selected_granularity}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    genre_app = GenreVisualizationApp()
    genre_app.show()
    sys.exit(app.exec_())
