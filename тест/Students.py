from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QMessageBox, QComboBox
import mysql.connector
from PyQt5.QtCore import pyqtSignal 

class EditDialog(QDialog):
    data_changed = pyqtSignal()

    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.student_id = None 
        self.setWindowTitle("Редактировать студента")
        self.setGeometry(200, 200, 400, 200)
        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()
        self.edit_inputs = []
        labels = ["Имя", "Фамилия", "Серия и номер паспорта", "Стоимость обучения",
                  "Дата рождения", "Адрес", "Номер телефона", "Email", "Дата поступления"]
        for label in labels:
            edit_input = QLineEdit()
            form_layout.addRow(label, edit_input)
            self.edit_inputs.append(edit_input)

        vehicle_query = "SELECT Vehicle_ID, Make, Model, Vehicle_Type FROM Vehicles"  # Добавлено поле 'Vehicle_Type' в запрос
        self.db_cursor.execute(vehicle_query)
        vehicle_data = self.db_cursor.fetchall()
        vehicles = [(f"{data[1]} {data[2]} ({data[3]})", data[0]) for data in vehicle_data]  # Добавлен 'Vehicle_Type'

        vehicle_combo = QComboBox()
        for vehicle in vehicles:
            vehicle_combo.addItem(vehicle[0], vehicle[1])

        form_layout.addRow("Выберите автомобиль", vehicle_combo)
        self.edit_inputs.append(vehicle_combo)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_data)
        form_layout.addRow(self.save_button)
        self.setLayout(form_layout)

    def save_data(self):
        new_data = [input_widget.text() for input_widget in self.edit_inputs[:-1]]
        vehicle_id = self.edit_inputs[-1].currentData()
        required_fields = [new_data[0], new_data[1], new_data[2], new_data[3],
                           new_data[4], new_data[5], new_data[6], new_data[7], new_data[8]]

        if not all(required_fields):
            QMessageBox.critical(self, "Ошибка", "Заполните все поля")
            return

        if self.student_id is not None:   # Проверка на наличие ID студента для редактирования
            query = """
            UPDATE Students
            SET `Vehicle_ID` = %s, `First_Name` = %s, `Last_Name` = %s, `Passport_Info` = %s,
                `Tuition_Cost` = %s, `Date_of_Birth` = %s, `Address` = %s, `Phone` = %s,
                `Email` = %s, `Enrollment_Date` = %s
            WHERE `Student_ID` = %s
            """
            data = (
                vehicle_id, new_data[0], new_data[1], new_data[2], new_data[3],
                new_data[4], new_data[5], new_data[6], new_data[7], new_data[8], self.student_id
            )

            try:
                self.db_cursor.execute(query, data)
                self.db_connection.commit()
                self.accept()
                self.data_changed.emit()  # Отправка сигнала при успешном сохранении
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {e}")
        else:
            query = """
            INSERT INTO Students (`Vehicle_ID`, `First_Name`, `Last_Name`, `Passport_Info`, `Tuition_Cost`,
                `Date_of_Birth`, `Address`, `Phone`, `Email`, `Enrollment_Date`, `Graduation_Date`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
            """
            data = (
                vehicle_id, new_data[0], new_data[1], new_data[2], new_data[3],
                new_data[4], new_data[5], new_data[6], new_data[7], new_data[8]
            )

            try:
                self.db_cursor.execute(query, data)
                self.db_connection.commit()
                self.accept()
                self.data_changed.emit()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении студента: {e}")
                
    def fill_fields(self, data):
        self.student_id = data[0]
        for field, value in zip(self.edit_inputs, data[4:]):
            if isinstance(field, QComboBox):
                field.setCurrentText(value)
            else:
                field.setText(value)

    def clear_fields(self):
        self.student_id = None
        for field in self.edit_inputs:
            if isinstance(field, QComboBox):
                field.setCurrentIndex(0)
            else:
                field.clear()

# Основной класс
class StudentsTab(QWidget):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.initUI()
        self.connect_signals()  # Вызов метода для подключения сигналов

    def connect_signals(self):
        # Этот метод подключает сигнал к слоту
        self.edit_student_button = EditDialog(self.db_connection, self.db_cursor)
        self.add_student_button = EditDialog(self.db_connection, self.db_cursor)
        self.edit_student_button.data_changed.connect(self.load_students_data)
        self.add_student_button.data_changed.connect(self.load_students_data)

    def initUI(self):
        students_layout = QVBoxLayout()
        self.table_students = QTableWidget()
        self.table_students.setColumnCount(13)
        self.table_students.setHorizontalHeaderLabels(["Студент ID", "Марка", "Модель", "Тип", "Имя", "Фамилия", "Серия и номер паспорта",
                                                      "Стоимость обучения", "Дата рождения", "Адрес", "Номер телефона",
                                                      "Email", "Дата поступления", "Дата окончания"])
        self.load_students_button = QPushButton("Загрузить данные")
        self.load_students_button.clicked.connect(self.load_students_data)
        self.students_search_input = QLineEdit()
        self.students_search_button = QPushButton("Поиск")
        self.students_search_button.clicked.connect(self.search_students)
        self.edit_student_button = QPushButton("Редактировать запись")
        self.edit_student_button.clicked.connect(self.edit_student_record)
        self.add_student_button = QPushButton("Добавить студента")
        self.add_student_button.clicked.connect(self.add_student)
        self.delete_student_button = QPushButton("Удалить запись")
        self.delete_student_button.clicked.connect(self.delete_student_record)
        students_layout.addWidget(self.load_students_button)
        students_layout.addWidget(self.students_search_input)
        students_layout.addWidget(self.students_search_button)
        students_layout.addWidget(self.edit_student_button)
        students_layout.addWidget(self.add_student_button)
        students_layout.addWidget(self.delete_student_button)
        students_layout.addWidget(self.table_students)
        self.setLayout(students_layout)

    def load_students_data(self):
        query = """
        SELECT Students.Student_ID, Vehicles.Make, Vehicles.Model, Vehicles.Vehicle_Type,
            Students.First_Name, Students.Last_Name, Students.Passport_Info,
            Students.Tuition_Cost, Students.Date_of_Birth, Students.Address,
            Students.Phone, Students.Email, Students.Enrollment_Date, Students.Graduation_Date
        FROM Students
        JOIN Vehicles ON Students.Vehicle_ID = Vehicles.Vehicle_ID
        """
        self.db_cursor.execute(query)
        result = self.db_cursor.fetchall()
        self.table_students.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table_students.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_students.setItem(row_num, col_num, item)

    def search_students(self):
        search_term = self.students_search_input.text()
        if not search_term:
            return

        query = "SELECT * FROM Students WHERE `First_Name` LIKE %s OR `Last_Name` LIKE %s"
        data = (f"%{search_term}%", f"%{search_term}%")
        self.db_cursor.execute(query, data)
        search_result = self.db_cursor.fetchall()

        self.table_students.setRowCount(0)

        for row_num, row_data in enumerate(search_result):
            self.table_students.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_students.setItem(row_num, col_num, item)

    def edit_student_record(self):
        selected_row = self.table_students.currentRow()
        if selected_row >= 0:
            data = [self.table_students.item(selected_row, col).text() for col in range(13)]
            edit_dialog = EditDialog(self.db_connection, self.db_cursor)
            edit_dialog.fill_fields(data)
            edit_dialog.exec()
        self.load_students_data()

    def add_student(self):
        add_dialog = EditDialog(self.db_connection, self.db_cursor)
        result = add_dialog.exec()

        if result == QDialog.Accepted:
            add_dialog.clear_fields()  # Очистка полей в диалоговом окне
            self.load_students_data()  # Обновление таблицы студентов

    def delete_student_record(self):
        selected_row = self.table_students.currentRow()
        if selected_row >= 0:
            student_id = self.table_students.item(selected_row, 0).text()

            query = "DELETE FROM Students WHERE `Student_ID` = %s"
            data = (student_id,)
            try:
                self.db_cursor.execute(query, data)
                self.db_connection.commit()
                self.load_students_data()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении студента: {e}")
