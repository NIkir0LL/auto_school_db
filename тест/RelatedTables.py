from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QLineEdit

class RelatedTablesTab(QWidget):
    def __init__(self, db_connection, db_cursor):
        super().__init__(parent=None)
        self.db_connection = db_connection
        self.db_cursor = db_cursor

        self.init_related_tables_tab()

    def init_related_tables_tab(self):
        headers = ["Студент ID", "Имя студента", "Фамилия студента", "Имя инструктора", "Фамилия инструктора", "Марка", "Модель", "Тип авто", "Время начала", "Продолжительность", "Результат экзамена", "Тип экзамена"]
        self.table_related = QTableWidget(0, len(headers))
        self.table_related.setHorizontalHeaderLabels(headers)

        self.load_related_data_button = QPushButton("Загрузить данные")
        self.load_related_data_button.clicked.connect(self.load_related_data)

        self.name_search_input = QLineEdit()
        self.name_search_button = QPushButton("Поиск по имени")
        self.name_search_button.clicked.connect(self.search_by_name)

        related_layout = QVBoxLayout()
        related_layout.addWidget(self.load_related_data_button)
        related_layout.addWidget(self.name_search_input)
        related_layout.addWidget(self.name_search_button)
        related_layout.addWidget(self.table_related)
        self.setLayout(related_layout)

    def load_related_data(self):
        query = """
        SELECT Students.Student_ID, Students.First_Name, Students.Last_Name, Instructors.First_Name, Instructors.Last_Name, 
        Vehicles.Make, Vehicles.Model, Vehicles.Vehicle_Type, Schedule.Start_Time, Schedule.Duration, 
        Exam_Results.Grade, Exam_Results.Exam_Type
        FROM Students
        LEFT JOIN Schedule ON Students.Student_ID = Schedule.Student_ID
        LEFT JOIN Vehicles ON Schedule.Vehicle_ID = Vehicles.Vehicle_ID
        LEFT JOIN Instructors ON Schedule.Instructor_ID = Instructors.Instructor_ID
        LEFT JOIN Exam_Results ON Students.Student_ID = Exam_Results.Student_ID
        """
        self.db_cursor.execute(query)
        result = self.db_cursor.fetchall()

        self.table_related.setRowCount(0)

        for row_num, row_data in enumerate(result):
            self.table_related.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_related.setItem(row_num, col_num, item)

    def search_by_name(self):
        name_to_search = self.name_search_input.text()
        if not name_to_search:
            return

        query = """
        SELECT Students.Student_ID, Students.First_Name, Students.Last_Name, Instructors.First_Name, Instructors.Last_Name, 
        Vehicles.Make, Vehicles.Model, Vehicles.Vehicle_Type, Schedule.Start_Time, Schedule.Duration, 
        Exam_Results.Grade, Exam_Results.Exam_Type
        FROM Students
        LEFT JOIN Schedule ON Students.Student_ID = Schedule.Student_ID
        LEFT JOIN Vehicles ON Schedule.Vehicle_ID = Vehicles.Vehicle_ID
        LEFT JOIN Instructors ON Schedule.Instructor_ID = Instructors.Instructor_ID
        LEFT JOIN Exam_Results ON Students.Student_ID = Exam_Results.Student_ID
        WHERE Students.First_Name LIKE %s OR Instructors.First_Name LIKE %s
        """

        data = (f"%{name_to_search}%", f"%{name_to_search}%")
        self.db_cursor.execute(query, data)
        result = self.db_cursor.fetchall()

        self.table_related.setRowCount(0)

        for row_num, row_data in enumerate(result):
            self.table_related.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_related.setItem(row_num, col_num, item)
