from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QDialog,
    QFormLayout, QMessageBox, QComboBox
)
from PyQt5.QtCore import pyqtSignal
import mysql.connector

class EditDialog(QDialog):
    data_changed = pyqtSignal()

    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.instructor_id = None
        self.setWindowTitle("Редактировать инструктора")
        self.setGeometry(200, 200, 400, 200)
        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()
        self.edit_inputs = []
        labels = ["Имя", "Фамилия", "Серия и номер паспорта", "Зарплата",
                  "Дата рождения", "Адрес", "Номер телефона", "Email", "Дата найма"]
        for label in labels:
            edit_input = QLineEdit()
            form_layout.addRow(label, edit_input)
            self.edit_inputs.append(edit_input)

        vehicle_query = "SELECT Vehicle_ID, Make, Model, Vehicle_Type FROM Vehicles"
        self.db_cursor.execute(vehicle_query)
        vehicle_data = self.db_cursor.fetchall()
        vehicles = [(f"{data[1]} {data[2]} ({data[3]})", data[0]) for data in vehicle_data]

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

        query = """
        UPDATE Instructors
        SET `Vehicle_ID` = %s, `First_Name` = %s, `Last_Name` = %s, `Passport_Info` = %s,
            `Salary` = %s, `Date_of_Birth` = %s, `Address` = %s, `Phone` = %s,
            `Email` = %s, `Hire_Date` = %s
        WHERE `Instructor_ID` = %s
        """ if self.instructor_id is not None else """
        INSERT INTO Instructors (`Vehicle_ID`, `First_Name`, `Last_Name`, `Passport_Info`, `Salary`,
            `Date_of_Birth`, `Address`, `Phone`, `Email`, `Hire_Date`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            vehicle_id, new_data[0], new_data[1], new_data[2], new_data[3],
            new_data[4], new_data[5], new_data[6], new_data[7], new_data[8], self.instructor_id
        ) if self.instructor_id is not None else (
            vehicle_id, new_data[0], new_data[1], new_data[2], new_data[3],
            new_data[4], new_data[5], new_data[6], new_data[7], new_data[8]
        )

        try:
            self.db_cursor.execute(query, data)
            self.db_connection.commit()
            self.accept()
            self.data_changed.emit()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {e}")

    def fill_fields(self, data):
        self.instructor_id = data[0]
        for field, value in zip(self.edit_inputs, data[4:]):
            if isinstance(field, QComboBox):
                field.setCurrentText(value)
            else:
                field.setText(value)

    def clear_fields(self):
        self.instructor_id = None
        for field in self.edit_inputs:
            if isinstance(field, QComboBox):
                field.setCurrentIndex(0)
            else:
                field.clear()

class InstructorsTab(QWidget):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.initUI()
        self.connect_signals()

    def connect_signals(self):
        self.edit_instructor_button = EditDialog(self.db_connection, self.db_cursor)
        self.add_instructor_button = EditDialog(self.db_connection, self.db_cursor)
        self.edit_instructor_button.data_changed.connect(self.load_instructors_data)
        self.add_instructor_button.data_changed.connect(self.load_instructors_data)

    def initUI(self):
        instructors_layout = QVBoxLayout()
        self.table_instructors = QTableWidget()
        self.table_instructors.setColumnCount(13)
        self.table_instructors.setHorizontalHeaderLabels([
            "Инструктор ID", "Марка", "Модель", "Тип", "Имя", "Фамилия", "Серия и номер паспорта",
            "Зарплата", "Дата рождения", "Адрес", "Номер телефона", "Email", "Дата найма"
        ])
        self.load_instructors_button = QPushButton("Загрузить данные")
        self.load_instructors_button.clicked.connect(self.load_instructors_data)
        self.instructors_search_input = QLineEdit()
        self.instructors_search_button = QPushButton("Поиск")
        self.instructors_search_button.clicked.connect(self.search_instructors)
        self.edit_instructor_button = QPushButton("Редактировать запись")
        self.edit_instructor_button.clicked.connect(self.edit_instructor_record)
        self.add_instructor_button = QPushButton("Добавить инструктора")
        self.add_instructor_button.clicked.connect(self.add_instructor)
        self.delete_instructor_button = QPushButton("Удалить запись")
        self.delete_instructor_button.clicked.connect(self.delete_instructor_record)
        instructors_layout.addWidget(self.load_instructors_button)
        instructors_layout.addWidget(self.instructors_search_input)
        instructors_layout.addWidget(self.instructors_search_button)
        instructors_layout.addWidget(self.edit_instructor_button)
        instructors_layout.addWidget(self.add_instructor_button)
        instructors_layout.addWidget(self.delete_instructor_button)
        instructors_layout.addWidget(self.table_instructors)
        self.setLayout(instructors_layout)

    def load_instructors_data(self):
        query = """
        SELECT Instructors.Instructor_ID, Vehicles.Make, Vehicles.Model, Vehicles.Vehicle_Type,
            Instructors.First_Name, Instructors.Last_Name, Instructors.Passport_Info,
            Instructors.Salary, Instructors.Date_of_Birth, Instructors.Address,
            Instructors.Phone, Instructors.Email, Instructors.Hire_Date
        FROM Instructors
        JOIN Vehicles ON Instructors.Vehicle_ID = Vehicles.Vehicle_ID
        """
        self.db_cursor.execute(query)
        result = self.db_cursor.fetchall()
        self.table_instructors.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table_instructors.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_instructors.setItem(row_num, col_num, item)

    def search_instructors(self):
        search_term = self.instructors_search_input.text()
        if not search_term:
            return

        query = "SELECT * FROM Instructors WHERE `First_Name` LIKE %s OR `Last_Name` LIKE %s"
        data = (f"%{search_term}%", f"%{search_term}%")
        self.db_cursor.execute(query, data)
        search_result = self.db_cursor.fetchall()

        self.table_instructors.setRowCount(0)

        for row_num, row_data in enumerate(search_result):
            self.table_instructors.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_instructors.setItem(row_num, col_num, item)

    def edit_instructor_record(self):
        selected_row = self.table_instructors.currentRow()
        if selected_row >= 0:
            data = [self.table_instructors.item(selected_row, col).text() for col in range(13)]
            edit_dialog = EditDialog(self.db_connection, self.db_cursor)
            edit_dialog.fill_fields(data)
            edit_dialog.exec()
        self.load_instructors_data()

    def add_instructor(self):
        add_dialog = EditDialog(self.db_connection, self.db_cursor)
        result = add_dialog.exec()

        if result == QDialog.Accepted:
            add_dialog.clear_fields()
            self.load_instructors_data()

    def delete_instructor_record(self):
        selected_row = self.table_instructors.currentRow()
        if selected_row >= 0:
            instructor_id = self.table_instructors.item(selected_row, 0).text()

            query = "DELETE FROM Instructors WHERE `Instructor_ID` = %s"
            data = (instructor_id,)
            try:
                self.db_cursor.execute(query, data)
                self.db_connection.commit()
                self.load_instructors_data()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении инструктора: {e}")
