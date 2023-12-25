from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QMessageBox, QComboBox

class EditExamResultsDialog(QDialog):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor

        self.setWindowTitle("Редактировать запись")
        self.setGeometry(200, 200, 400, 200)

        # Определение необходимых атрибутов
        self.student_combobox = QComboBox()
        self.vehicle_combobox = QComboBox()
        self.instructor_combobox = QComboBox()
        self.edit_inputs = []
        self.exam_type_combobox = QComboBox()
        self.grade_combobox = QComboBox()

        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()
        self.edit_inputs = []

        labels = ["Дата экзамена"]

        self.student_combobox = QComboBox()
        self.vehicle_combobox = QComboBox()
        self.instructor_combobox = QComboBox()

        form_layout.addRow("Студент", self.student_combobox)
        form_layout.addRow("Машина", self.vehicle_combobox)
        form_layout.addRow("Инструктор", self.instructor_combobox)

        for label in labels:
            edit_input = QLineEdit() if label == "Дата экзамена" else QComboBox()
            form_layout.addRow(label, edit_input)
            self.edit_inputs.append(edit_input)

        self.exam_type_combobox = QComboBox()
        self.exam_type_combobox.addItem("Тест")
        self.exam_type_combobox.addItem("Практика")
        form_layout.addRow("Тип экзамена", self.exam_type_combobox)

        self.grade_combobox = QComboBox()
        self.grade_combobox.addItem("Сдано")
        self.grade_combobox.addItem("Несдано")
        form_layout.addRow("Оценка", self.grade_combobox)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_data)
        form_layout.addRow(self.save_button)

        self.setLayout(form_layout)

        self.populate_students()
        self.populate_vehicles()
        self.populate_instructors()

        self.student_combobox.currentIndexChanged.connect(self.student_combobox_changed)

    def populate_students(self):
        query = "SELECT Student_ID, First_Name, Last_Name, Vehicle_ID FROM Students"
        self.db_cursor.execute(query)
        students = self.db_cursor.fetchall()

        for student in students:
            full_name = f"{student[1]} {student[2]}"
            self.student_combobox.addItem(full_name, userData=(student[0], student[3]))

    def populate_vehicles(self):
        query = "SELECT Vehicle_ID, Make, Model FROM Vehicles"
        self.db_cursor.execute(query)
        vehicles = self.db_cursor.fetchall()

        for vehicle in vehicles:
            full_name = f"{vehicle[1]} {vehicle[2]}"
            self.vehicle_combobox.addItem(full_name, userData=(vehicle[0],))

    def populate_instructors(self):
        query = "SELECT Instructor_ID, First_Name, Last_Name FROM Instructors"
        self.db_cursor.execute(query)
        instructors = self.db_cursor.fetchall()

        for instructor in instructors:
            full_name = f"{instructor[1]} {instructor[2]}"
            self.instructor_combobox.addItem(full_name, userData=(instructor[0],))

    def set_data(self, data):
        student_id, vehicle_id, instructor_id = data[:3]
        
        index_student = self.student_combobox.findData((student_id, vehicle_id))
        self.student_combobox.setCurrentIndex(index_student)

        index_vehicle = self.vehicle_combobox.findData(vehicle_id)
        self.vehicle_combobox.setCurrentIndex(index_vehicle)

        index_instructor = self.instructor_combobox.findData(instructor_id)
        self.instructor_combobox.setCurrentIndex(index_instructor)

        for input_widget, value in zip(self.edit_inputs, data[3:6]):
            input_widget.setText(str(value))

        exam_type_index = self.exam_type_combobox.findText(data[6])
        self.exam_type_combobox.setCurrentIndex(exam_type_index)

        grade_index = self.grade_combobox.findText(data[7])
        self.grade_combobox.setCurrentIndex(grade_index)

    def student_combobox_changed(self):
        student_info = self.student_combobox.currentData()
        if student_info:
            vehicle_id = student_info[1]
            instructor_id = self.get_instructor_for_vehicle(vehicle_id)

            # Обновление информации о машине
            index_vehicle = self.vehicle_combobox.findData(vehicle_id)
            self.vehicle_combobox.setCurrentIndex(index_vehicle)

            # Обновление информации об инструкторе
            index_instructor = self.instructor_combobox.findData(instructor_id)
            self.instructor_combobox.setCurrentIndex(index_instructor)

    def get_instructor_for_vehicle(self, vehicle_id):
        query = "SELECT Instructor_ID FROM Instructors WHERE Vehicle_ID = %s"
        self.db_cursor.execute(query, (vehicle_id,))
        instructor_id = self.db_cursor.fetchone()
        return instructor_id[0] if instructor_id else None

    def save_data(self):
        student_data = self.student_combobox.currentData()
        vehicle_data = self.vehicle_combobox.currentData()
        instructor_data = self.instructor_combobox.currentData()

        student_id = student_data[0] if student_data else None
        vehicle_id = vehicle_data[0] if vehicle_data else None
        instructor_id = instructor_data[0] if instructor_data else None

        new_data = [
            student_id,
            vehicle_id,
            instructor_id,
        ] + [input_widget.text() for input_widget in self.edit_inputs]

        exam_type = self.exam_type_combobox.currentText()
        grade = self.grade_combobox.currentText()

        if not all(new_data[1:]):
            QMessageBox.critical(self, "Ошибка", "Все поля, кроме студента, должны быть заполнены.")
            return

        query = """
        UPDATE Exam_Results
        SET `Vehicle_ID` = %s,
            `Examiner_ID` = %s,
            `Exam_Date` = %s,
            `Exam_Type` = %s,
            `Grade` = %s
        WHERE `Result_ID` = %s
        """

        data = (
            new_data[1], new_data[2], new_data[3], exam_type, grade, new_data[0]
        )

        self.db_cursor.execute(query, data)
        self.db_connection.commit()
        self.accept()

class ExamResultsTab(QWidget):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.initUI()

    def initUI(self):
        exam_results_layout = QVBoxLayout()

        self.table_exam_results = QTableWidget()
        self.table_exam_results.setColumnCount(13)  
        self.table_exam_results.setHorizontalHeaderLabels([
            "Результат ID", "Инструктор", "Имя инструктора", "Фамилия инструктора",
            "Студент", "Имя студента", "Фамилия студента",
            "Авто", "Марка авто", "Модель авто", "Дата экзамена", "Тип экзамена", "Оценка"
        ])

        self.load_exam_results_button = QPushButton("Загрузить данные")
        self.load_exam_results_button.clicked.connect(self.load_exam_results_data)

        self.exam_results_search_input = QLineEdit()
        self.exam_results_search_button = QPushButton("Поиск")
        self.exam_results_search_button.clicked.connect(self.search_exam_results)

        self.edit_exam_results_button = QPushButton("Редактировать запись")
        self.edit_exam_results_button.clicked.connect(self.edit_exam_results_record)

        self.add_exam_results_button = QPushButton("Добавить результат экзамена")
        self.add_exam_results_button.clicked.connect(self.add_exam_results)

        self.delete_exam_results_button = QPushButton("Удалить запись")
        self.delete_exam_results_button.clicked.connect(self.delete_exam_results)

        exam_results_layout.addWidget(self.load_exam_results_button)
        exam_results_layout.addWidget(self.exam_results_search_input)
        exam_results_layout.addWidget(self.exam_results_search_button)
        exam_results_layout.addWidget(self.edit_exam_results_button)
        exam_results_layout.addWidget(self.add_exam_results_button)
        exam_results_layout.addWidget(self.delete_exam_results_button)
        exam_results_layout.addWidget(self.table_exam_results)

        for col_index in [1, 4, 7]:
            self.table_exam_results.setColumnHidden(col_index, True)

        self.setLayout(exam_results_layout)

    def load_exam_results_data(self):
        query = """
        SELECT e.Result_ID, e.Examiner_ID, i.First_Name AS Instructor_First_Name,
               i.Last_Name AS Instructor_Last_Name,
               e.Student_ID, s.First_Name AS Student_First_Name, s.Last_Name AS Student_Last_Name,
               e.Vehicle_ID, v.Make, v.Model,
               e.Exam_Date, e.Exam_Type, e.Grade
        FROM Exam_Results e
        LEFT JOIN Instructors i ON e.Examiner_ID = i.Instructor_ID
        LEFT JOIN Students s ON e.Student_ID = s.Student_ID
        LEFT JOIN Vehicles v ON e.Vehicle_ID = v.Vehicle_ID
        """
        self.db_cursor.execute(query)
        result = self.db_cursor.fetchall()
        self.table_exam_results.setRowCount(0)

        for row_num, row_data in enumerate(result):
            self.table_exam_results.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_exam_results.setItem(row_num, col_num, item)


    def search_exam_results(self):
        search_term = self.exam_results_search_input.text()
        if not search_term:
            return

        query = """
        SELECT e.Result_ID, e.Student_ID, e.Examiner_ID, e.Vehicle_ID, e.Exam_Date, e.Exam_Type, e.Grade,
               s.First_Name AS Student_First_Name, s.Last_Name AS Student_Last_Name
        FROM Exam_Results e
        LEFT JOIN Students s ON e.Student_ID = s.Student_ID
        WHERE s.First_Name LIKE %s OR s.Last_Name LIKE %s
        """
        data = (f"%{search_term}%", f"%{search_term}%")
        self.db_cursor.execute(query, data)
        search_result = self.db_cursor.fetchall()

        self.table_exam_results.setRowCount(0)

        for row_num, row_data in enumerate(search_result):
            self.table_exam_results.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_exam_results.setItem(row_num, col_num, item)

    def edit_exam_results_record(self):
        selected_row = self.table_exam_results.currentRow()
        if selected_row >= 0:
            data = [self.table_exam_results.item(selected_row, col).text() for col in range(7, 9)]
            edit_dialog = EditExamResultsDialog(self.db_connection, self.db_cursor)
            edit_dialog.set_data(data)
            result = edit_dialog.exec()

            if result == QDialog.Accepted:
                student_data = edit_dialog.student_combobox.currentData()
                vehicle_data = edit_dialog.vehicle_combobox.currentData()
                instructor_data = edit_dialog.instructor_combobox.currentData()

                student_id = student_data[0] if student_data else None
                vehicle_id = vehicle_data[0] if vehicle_data else None
                instructor_id = instructor_data[0] if instructor_data else None

                new_data = [
                    student_id,
                    vehicle_id,
                    instructor_id,
                ] + [edit_dialog.edit_inputs[i].text() for i in range(3)]

                exam_type = edit_dialog.exam_type_combobox.currentText()
                grade = edit_dialog.grade_combobox.currentText()

                if not all(new_data[1:]):
                    QMessageBox.critical(self, "Ошибка", "Все поля, кроме студента, должны быть заполнены.")
                    return

                query = """
                UPDATE Exam_Results
                SET `Vehicle_ID` = %s,
                    `Examiner_ID` = %s,
                    `Exam_Date` = %s,
                    `Exam_Type` = %s,
                    `Grade` = %s
                WHERE `Result_ID` = %s
                """
                data = (
                    new_data[1], new_data[2], new_data[3], exam_type, grade, new_data[0]
                )

                self.db_cursor.execute(query, data)
                self.db_connection.commit()
                self.load_exam_results_data()

    def add_exam_results(self):
        add_dialog = EditExamResultsDialog(self.db_connection, self.db_cursor)
        result = add_dialog.exec()

        if result == QDialog.Accepted:
            student_data = add_dialog.student_combobox.currentData()
            vehicle_data = add_dialog.vehicle_combobox.currentData()
            instructor_data = add_dialog.instructor_combobox.currentData()

            student_id = student_data[0] if student_data else None
            vehicle_id = vehicle_data[0] if vehicle_data else None
            instructor_id = instructor_data[0] if instructor_data else None

            new_data = [student_id, vehicle_id, instructor_id] + [add_dialog.edit_inputs[i].text() for i in range(min(3, len(add_dialog.edit_inputs)))]

            exam_type = add_dialog.exam_type_combobox.currentText()
            grade = add_dialog.grade_combobox.currentText()

            if not all(new_data[1:]):
                QMessageBox.critical(self, "Ошибка", "Все поля, кроме студента, должны быть заполнены.")
                return

            query = """
            INSERT INTO Exam_Results (`Student_ID`, `Vehicle_ID`, `Examiner_ID`, `Exam_Date`, `Exam_Type`, `Grade`)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (
                new_data[0], new_data[1], new_data[2], new_data[3], exam_type, grade
            )

            self.db_cursor.execute(query, data)
            self.db_connection.commit()
            self.load_exam_results_data()

    def delete_exam_results(self):
        selected_row = self.table_exam_results.currentRow()
        if selected_row >= 0:
            result_id = self.table_exam_results.item(selected_row, 0).text()
            query = "DELETE FROM Exam_Results WHERE `Result_ID` = %s"
            self.db_cursor.execute(query, (result_id,))
            self.db_connection.commit()
            self.load_exam_results_data()



