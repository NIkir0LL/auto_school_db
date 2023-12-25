from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, \
    QTableWidgetItem, QDialog, QFormLayout, QMessageBox, QComboBox

class SelectStudentDialog(QDialog):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor

        self.setWindowTitle("Выбрать студента")
        self.setGeometry(200, 200, 400, 200)

        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        self.student_combo = QComboBox()

        layout.addRow("Выберите студента:", self.student_combo)

        select_button = QPushButton("Выбрать")
        select_button.clicked.connect(self.accept)
        layout.addRow(select_button)

        self.setLayout(layout)

    def exec_(self):
        self.load_student_data()
        return super().exec_()

    def load_student_data(self):
        query = "SELECT Student_ID, First_Name, Last_Name FROM Students"
        self.db_cursor.execute(query)
        students = self.db_cursor.fetchall()

        for student in students:
            self.student_combo.addItem(f"{student[1]} {student[2]}", userData=student[0])


class EditScheduleDialog(QDialog):
    def __init__(self, db_connection, db_cursor, load_schedule_data_callback):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.schedule_id = None
        self.edit_inputs = []
        self.load_schedule_data_callback = load_schedule_data_callback

        self.setWindowTitle("Редактировать запись")
        self.setGeometry(200, 200, 400, 200)

        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()
        self.edit_inputs = []

        labels = ["Инструктор", "Студент", "Авто", "Дата и время начала", "Продолжительность"]

        for label in labels:
            if label in ["Инструктор", "Студент", "Авто"]:
                combo_box = QComboBox()
                form_layout.addRow(label, combo_box)
                self.edit_inputs.append(combo_box)
            else:
                edit_input = QLineEdit()
                form_layout.addRow(label, edit_input)
                self.edit_inputs.append(edit_input)

        form_layout.addRow(QPushButton("Сохранить", clicked=self.save_data))

        self.setLayout(form_layout)

        self.load_data_to_combo_box(self.edit_inputs[0], "Instructors", "Instructor_ID", "First_Name, Last_Name")
        self.load_data_to_combo_box(self.edit_inputs[1], "Students", "Student_ID", "First_Name, Last_Name")
        self.load_data_to_combo_box(self.edit_inputs[2], "Vehicles", "Vehicle_ID", "Make, Model, Vehicle_Type")

    def load_data_to_combo_box(self, combo_box, table_name, id_column, display_columns):
        query = f"SELECT {id_column}, {display_columns} FROM {table_name}"
        self.db_cursor.execute(query)
        data = self.db_cursor.fetchall()
        for row in data:
            display_text = ', '.join(str(x) for x in row[1:])
            combo_box.addItem(display_text, userData=row[0])

    def set_data(self, data):
        self.schedule_id = data[0] if data[0] is not None else -1
        for input_widget, value in zip(self.edit_inputs, data[1:]):
            if isinstance(input_widget, QComboBox):
                index = input_widget.findData(int(value))
                if index != -1:
                    input_widget.setCurrentIndex(index)
            else:
                input_widget.setText(str(value))

    def save_data(self):
        new_data = [int(self.schedule_id) if self.schedule_id is not None else -1] + [
            input_widget.currentData() if isinstance(input_widget, QComboBox) else str(input_widget.text())
            for input_widget in self.edit_inputs
        ]

        if not all(new_data[2:]):
            QMessageBox.critical(self, "Ошибка", "Все поля, кроме Расписания ID, должны быть заполнены.")
            return

        query = """
        UPDATE Schedule
        SET `Instructor_ID` = %s,
            `Student_ID` = %s,
            `Vehicle_ID` = %s,
            `Start_Time` = %s,
            `Duration` = %s
        WHERE `Schedule_ID` = %s
        """

        data = (
            int(new_data[1]), int(new_data[2]), int(new_data[3]), str(new_data[4]), int(new_data[5]), int(new_data[0])
        )

        try:
            self.db_cursor.execute(query, data)
            self.db_connection.commit()
            self.load_schedule_data_callback()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {str(e)}")


class ScheduleTab(QWidget):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.initUI()

    def initUI(self):
        schedule_layout = QVBoxLayout()

        self.table_schedule = QTableWidget()
        self.table_schedule.setColumnCount(12)
        self.table_schedule.setHorizontalHeaderLabels([
            "Расписание ID", "Инструктор ID", "Имя инструктора", "Фамилия инструктора",
            "Студент ID", "Имя студента", "Фамилия студента",
            "Авто ID", "Марка авто", "Модель авто",
            "Дата и время начала", "Продолжительность"
        ])

        self.load_schedule_button = QPushButton("Загрузить данные")
        self.load_schedule_button.clicked.connect(self.load_schedule_data)

        self.schedule_search_input = QLineEdit()
        self.schedule_search_button = QPushButton("Поиск")
        self.schedule_search_button.clicked.connect(self.search_schedule)

        self.edit_schedule_button = QPushButton("Редактировать запись")
        self.edit_schedule_button.clicked.connect(self.edit_schedule_record)

        self.add_schedule_button = QPushButton("Добавить запись в расписание")
        self.add_schedule_button.clicked.connect(self.add_schedule)

        self.delete_schedule_button = QPushButton("Удалить запись из расписания")
        self.delete_schedule_button.clicked.connect(self.delete_schedule_record)

        schedule_layout.addWidget(self.load_schedule_button)
        schedule_layout.addWidget(self.schedule_search_input)
        schedule_layout.addWidget(self.schedule_search_button)
        schedule_layout.addWidget(self.edit_schedule_button)
        schedule_layout.addWidget(self.add_schedule_button)
        schedule_layout.addWidget(self.delete_schedule_button)
        schedule_layout.addWidget(self.table_schedule)

        for col_index in [1, 4, 7]:
            self.table_schedule.setColumnHidden(col_index, True)

        self.setLayout(schedule_layout)

    def load_schedule_data(self):
        query = """
        SELECT 
            Schedule.Schedule_ID,
            Schedule.Instructor_ID,
            Instructors.First_Name AS Instructor_First_Name,
            Instructors.Last_Name AS Instructor_Last_Name,
            Schedule.Student_ID,
            Students.First_Name AS Student_First_Name,
            Students.Last_Name AS Student_Last_Name,
            Schedule.Vehicle_ID,
            Vehicles.Make AS Vehicle_Make,
            Vehicles.Model AS Vehicle_Model,
            Schedule.Start_Time,
            Schedule.Duration
        FROM Schedule
        JOIN Instructors ON Schedule.Instructor_ID = Instructors.Instructor_ID
        JOIN Students ON Schedule.Student_ID = Students.Student_ID
        JOIN Vehicles ON Schedule.Vehicle_ID = Vehicles.Vehicle_ID
        WHERE Schedule.Instructor_ID = Instructors.Instructor_ID
            AND Schedule.Student_ID = Students.Student_ID
            AND Schedule.Vehicle_ID = Vehicles.Vehicle_ID
        """
        try:
            self.db_cursor.execute(query)
            result = self.db_cursor.fetchall()

            self.table_schedule.setRowCount(0)

            for row_num, row_data in enumerate(result):
                self.table_schedule.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.table_schedule.setItem(row_num, col_num, item)
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных: {str(e)}")

    def search_schedule(self):
        search_term = self.schedule_search_input.text()
        if not search_term:
            return

        query = "SELECT * FROM Schedule WHERE `Instructor_ID` LIKE %s OR `Student_ID` LIKE %s"
        data = (f"%{search_term}%", f"%{search_term}%")
        self.db_cursor.execute(query, data)
        search_result = self.db_cursor.fetchall()

        self.table_schedule.setRowCount(0)

        for row_num, row_data in enumerate(search_result):
            self.table_schedule.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_schedule.setItem(row_num, col_num, item)

    def edit_schedule_record(self):
        selected_row = self.table_schedule.currentRow()
        if selected_row >= 0:
            data = [self.table_schedule.item(selected_row, col).text() for col in range(12)]

            edit_dialog = EditScheduleDialog(self.db_connection, self.db_cursor, self.load_schedule_data)
            edit_dialog.set_data(data)
            result = edit_dialog.exec_()

            if result == QDialog.Accepted:
                new_data = [edit_dialog.edit_inputs[i].text() for i in range(6)]

                if not all(new_data[1:]):
                    QMessageBox.critical(self, "Ошибка", "Все поля, кроме Расписания ID, должны быть заполнены.")
                    return

                query = """
                UPDATE Schedule
                SET `Instructor_ID` = %s,
                    `Student_ID` = %s,
                    `Vehicle_ID` = %s,
                    `Start_Time` = %s,
                    `Duration` = %s
                WHERE `Schedule_ID` = %s
                """
                data = (
                    int(new_data[1]), int(new_data[2]), int(new_data[3]), str(new_data[4]),
                    int(new_data[5]), int(new_data[0])
                )

                try:
                    self.db_cursor.execute(query, data)
                    self.db_connection.commit()
                    self.load_schedule_data()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {str(e)}")

    def delete_schedule_record(self):
        selected_row = self.table_schedule.currentRow()
        if selected_row >= 0:
            schedule_id = int(self.table_schedule.item(selected_row, 0).text())

            query = "DELETE FROM Schedule WHERE Schedule_ID = %s"
            data = (schedule_id,)

            self.db_cursor.execute(query, data)
            self.db_connection.commit()

            self.load_schedule_data()

    def add_schedule(self):
        add_dialog = EditScheduleDialog(self.db_connection, self.db_cursor, self.load_schedule_data)
        result = add_dialog.exec_()

        if result == QDialog.Accepted:
            # Используйте currentData() для получения выбранных данных из QComboBox
            new_data = [add_dialog.edit_inputs[i].currentData() if isinstance(add_dialog.edit_inputs[i], QComboBox) else add_dialog.edit_inputs[i].text() for i in range(5)]

            if not all(new_data):
                QMessageBox.critical(self, "Ошибка", "Все поля должны быть заполнены.")
                return

            query = """
            INSERT INTO Schedule (`Instructor_ID`, `Student_ID`, `Vehicle_ID`, `Start_Time`, `Duration`)
            VALUES (%s, %s, %s, %s, %s)
            """
            data = (
                int(new_data[0]), int(new_data[1]), int(new_data[2]), str(new_data[3]), int(new_data[4])
            )

            try:
                self.db_cursor.execute(query, data)
                self.db_connection.commit()
                self.load_schedule_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении записи: {str(e)}")
