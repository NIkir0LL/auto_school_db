from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QMessageBox

class EditVehicleDialog(QDialog):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor

        self.setWindowTitle("Редактировать запись")
        self.setGeometry(200, 200, 400, 200)

        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()
        self.edit_inputs = []

        # Создаем поля ввода для каждой колонки
        labels = ["Авто ID", "Марка", "Модель", "Год", "Гос. номер", "Тип (мех, авто)", "VIN-номер"]
        for label in labels:
            edit_input = QLineEdit()
            form_layout.addRow(label, edit_input)
            self.edit_inputs.append(edit_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_data)
        form_layout.addRow(self.save_button)

        self.setLayout(form_layout)

    def set_data(self, data):
        # Заполняем поля ввода текущими данными
        for input_widget, value in zip(self.edit_inputs, data):
            input_widget.setText(str(value))

    def save_data(self):
        # Получаем новые значения из полей ввода
        new_data = [input_widget.text() for input_widget in self.edit_inputs]

        if not all(new_data[1:]):  # Check if any field (except Vehicle_ID) is empty
            QMessageBox.critical(self, "Ошибка", "Все поля, кроме Авто ID, должны быть заполнены.")
            return

        # Выполняем запрос на обновление данных в базе данных
        query = """
        UPDATE Vehicles
        SET `Make` = %s,
            `Model` = %s,
            `Year` = %s,
            `License_Plate` = %s,
            `Vehicle_Type` = %s,
            `VIN_Number` = %s
        WHERE `Vehicle_ID` = %s
        """

        # Преобразуем значения в кортеж для запроса
        data = (
            new_data[1], new_data[2], new_data[3], new_data[4],
            new_data[5], new_data[6], new_data[0]
        )

        self.db_cursor.execute(query, data)
        self.db_connection.commit()  # Подтверждаем изменения

        # Закрываем диалоговое окно после сохранения
        self.accept()

class VehiclesTab(QWidget):
    def __init__(self, db_connection, db_cursor):
        super().__init__()
        self.db_connection = db_connection
        self.db_cursor = db_cursor
        self.initUI()

    def initUI(self):
        vehicles_layout = QVBoxLayout()

        self.table_vehicles = QTableWidget()
        self.table_vehicles.setColumnCount(7)
        self.table_vehicles.setHorizontalHeaderLabels(["Авто ID", "Марка", "Модель", "Год", "Гос. номер", "Тип", "VIN-номер"])

        self.load_vehicles_button = QPushButton("Загрузить данные")
        self.load_vehicles_button.clicked.connect(self.load_vehicles_data)

        self.vehicles_search_input = QLineEdit()
        self.vehicles_search_button = QPushButton("Поиск")
        self.vehicles_search_button.clicked.connect(self.search_vehicles)

        self.edit_vehicle_button = QPushButton("Редактировать запись")
        self.edit_vehicle_button.clicked.connect(self.edit_vehicle_record)

        self.add_vehicle_button = QPushButton("Добавить автомобиль")
        self.add_vehicle_button.clicked.connect(self.add_vehicle)

        self.delete_vehicle_button = QPushButton("Удалить автомобиль")
        self.delete_vehicle_button.clicked.connect(self.delete_vehicle_record)

        vehicles_layout.addWidget(self.load_vehicles_button)
        vehicles_layout.addWidget(self.vehicles_search_input)
        vehicles_layout.addWidget(self.vehicles_search_button)
        vehicles_layout.addWidget(self.edit_vehicle_button)
        vehicles_layout.addWidget(self.add_vehicle_button)
        vehicles_layout.addWidget(self.delete_vehicle_button)
        vehicles_layout.addWidget(self.table_vehicles)

        self.setLayout(vehicles_layout)

    def load_vehicles_data(self):
        # Выполнение запроса для получения данных из таблицы "Vehicles"
        query = "SELECT * FROM Vehicles"
        self.db_cursor.execute(query)
        result = self.db_cursor.fetchall()

        # Очистка таблицы перед загрузкой новых данных
        self.table_vehicles.setRowCount(0)

        # Заполнение таблицы полученными данными
        for row_num, row_data in enumerate(result):
            self.table_vehicles.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_vehicles.setItem(row_num, col_num, item)

    def search_vehicles(self):
        search_term = self.vehicles_search_input.text()
        if not search_term:
            return

        # Поиск данных в таблице "Vehicles" по заданному критерию (например, по марке или гос. номеру)
        query = "SELECT * FROM Vehicles WHERE `Make` LIKE %s OR `License_Plate` LIKE %s"
        data = (f"%{search_term}%", f"%{search_term}%")
        self.db_cursor.execute(query, data)
        search_result = self.db_cursor.fetchall()

        self.table_vehicles.setRowCount(0)  # Очистить таблицу перед загрузкой результатов поиска

        for row_num, row_data in enumerate(search_result):
            self.table_vehicles.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_vehicles.setItem(row_num, col_num, item)

    def edit_vehicle_record(self):
        selected_row = self.table_vehicles.currentRow()
        if selected_row >= 0:
            # Получаем данные выбранной записи
            data = [self.table_vehicles.item(selected_row, col).text() for col in range(7)]

            # Создаем и открываем диалоговое окно для редактирования данных,
            # передавая ему соединение с базой данных и курсор
            edit_dialog = EditVehicleDialog(self.db_connection, self.db_cursor)
            edit_dialog.set_data(data)
            result = edit_dialog.exec()

            if result == QDialog.Accepted:
                # Получаем обновленные данные из диалогового окна
                new_data = [edit_dialog.edit_inputs[i].text() for i in range(7)]

                if not all(new_data[1:]):  # Check if any field (except Vehicle_ID) is empty
                    QMessageBox.critical(self, "Ошибка", "Все поля, кроме Авто ID, должны быть заполнены.")
                    return

                # Здесь можно выполнить запрос на обновление данных в базе данных
                query = """
                UPDATE Vehicles
                SET `Make` = %s,
                    `Model` = %s,
                    `Year` = %s,
                    `License_Plate` = %s,
                    `Vehicle_Type` = %s,
                    `VIN_Number` = %s
                WHERE `Vehicle_ID` = %s
                """
                data = (
                    new_data[1], new_data[2], new_data[3], new_data[4],
                    new_data[5], new_data[6], new_data[0]
                )

                self.db_cursor.execute(query, data)
                self.db_connection.commit()  # Подтверждаем изменения

                # После обновления, перезагружаем данные
                self.load_vehicles_data()

    def delete_vehicle_record(self):
        selected_row = self.table_vehicles.currentRow()
        if selected_row >= 0:
            vehicle_id = int(self.table_vehicles.item(selected_row, 0).text())
            
            # Выполнить запрос на удаление записи из базы данных
            query = "DELETE FROM Vehicles WHERE Vehicle_ID = %s"
            data = (vehicle_id,)
            
            self.db_cursor.execute(query, data)
            self.db_connection.commit()  # Подтвердить изменения
            
            # После удаления обновите таблицу, чтобы отобразить изменения
            self.load_vehicles_data()

    def add_vehicle(self):
        add_dialog = EditVehicleDialog(self.db_connection, self.db_cursor)
        result = add_dialog.exec()
    
        if result == QDialog.Accepted:
            new_data = [add_dialog.edit_inputs[i].text() for i in range(7)]
    
            if not all(new_data[1:]):
                QMessageBox.critical(self, "Ошибка", "Все поля, кроме Авто ID, должны быть заполнены.")
                return
    
            query = """
            INSERT INTO Vehicles (`Make`, `Model`, `Year`, `License_Plate`, `Vehicle_Type`, `VIN_Number`)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (
                new_data[1], new_data[2], new_data[3], new_data[4],
                new_data[5], new_data[6]
            )
    
            self.db_cursor.execute(query, data)
            self.db_connection.commit()
            self.load_vehicles_data()
