import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QLineEdit, QDialog, QFormLayout, QTabWidget
import mysql.connector

from Students import StudentsTab
from Instructors import InstructorsTab
from Vehicles import VehiclesTab
from Schedule import ScheduleTab
from ExamResults import ExamResultsTab
##from RelatedTables import RelatedTablesTab

class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление базой данных")
        self.setGeometry(100, 100, 1000, 600)

        # Устанавливаем соединение с базой данных
        self.db_connection = mysql.connector.connect(
            host='127.0.0.1',
            user="auto_school_user",
            password="auto_school_password",
            database="auto_school"
        )
        self.db_cursor = self.db_connection.cursor()

        self.initUI()

    def initUI(self):
        self.tab_students = StudentsTab(self.db_connection, self.db_cursor)
        self.tab_instructors = InstructorsTab(self.db_connection, self.db_cursor)
        self.tab_vehicles = VehiclesTab(self.db_connection, self.db_cursor)
        self.tab_schedule = ScheduleTab(self.db_connection, self.db_cursor)
        self.tab_exam_results = ExamResultsTab(self.db_connection, self.db_cursor)
        ##self.tab_related_tables = RelatedTablesTab(self.db_connection, self.db_cursor)
        tab_widget = QTabWidget()
        tab_widget.addTab(self.tab_students, "Студенты")
        tab_widget.addTab(self.tab_instructors, "Инструкторы")
        tab_widget.addTab(self.tab_vehicles, "Автомобили")
        tab_widget.addTab(self.tab_schedule, "Расписание занятий")
        tab_widget.addTab(self.tab_exam_results, "Результаты экзаменов")
        ##tab_widget.addTab(self.tab_related_tables, "Связанные Таблицы")

        self.setCentralWidget(tab_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())