CREATE DATABASE DrivingSchool;

USE DrivingSchool; 

-- Таблица "Студенты"
CREATE TABLE Students (
    Student_ID INT AUTO_INCREMENT PRIMARY KEY,
    Vehicle_ID INT,
    First_Name VARCHAR(50),
    Last_Name VARCHAR(50),
    Passport_Info INT,
    Tuition_Cost INT,
    Date_of_Birth DATE,
    Address VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(100),
    Enrollment_Date DATE,
    Graduation_Date DATE
);

-- Таблица "Инструкторы"
CREATE TABLE Instructors (
    Instructor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Vehicle_ID INT,
    First_Name VARCHAR(50),
    Last_Name VARCHAR(50),
    Passport_Info VARCHAR(100),
    Salary DECIMAL(10, 2),
    Date_of_Birth DATE,
    Address VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(100),
    Hire_Date DATE
);

-- Таблица "Автомобили"
CREATE TABLE Vehicles (
    Vehicle_ID INT AUTO_INCREMENT PRIMARY KEY,
    Make VARCHAR(50),
    Model VARCHAR(50),
    Year INT,
    License_Plate VARCHAR(20),
    Vehicle_Type VARCHAR(20),
    VIN_Number VARCHAR(17)
);

-- Таблица "Расписание занятий"
CREATE TABLE Schedule (
    Schedule_ID INT AUTO_INCREMENT PRIMARY KEY,
    Instructor_ID INT,
    Student_ID INT,
    Vehicle_ID INT,
    Start_Time DATETIME,
    Duration INT
);

-- Таблица "Результаты экзаменов"
CREATE TABLE Exam_Results (
    Result_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT,
    Examiner_ID INT,
    Vehicle_ID INT,
    Exam_Date DATE,
    Exam_Type VARCHAR(20),
    Grade VARCHAR(10)
);





-- добавление информации в бд

INSERT INTO Students (Vehicle_ID, First_Name, Last_Name, Passport_Info, Tuition_Cost, Date_of_Birth, Address, Phone, Email, Enrollment_Date, Graduation_Date) 
VALUES (1, 'Иван', 'Петров', 1234567890, 5000, '1995-03-15', 'Адрес', '123-456-7890', 'ivan@example.com', '2023-01-15', '2023-12-31');
INSERT INTO Instructors (Vehicle_ID, First_Name, Last_Name, Passport_Info, Salary, Date_of_Birth, Address, Phone, Email, Hire_Date) 
VALUES (1, 'Анна', 'Сидорова', 'AB1234567', 3000.50, '1985-05-20', 'Другой адрес', '987-654-3210', 'anna@example.com', '2023-01-10');
INSERT INTO Vehicles (Make, Model, Year, License_Plate, Vehicle_Type, VIN_Number) 
VALUES ('Toyota', 'Camry', 2023, 'ABC123', 'Седан', '1234567890ABCDEF');
INSERT INTO Schedule (Instructor_ID, Student_ID, Vehicle_ID, Start_Time, Duration) 
VALUES (1, 1, 1, '2023-02-15 10:00:00', 60);
INSERT INTO Exam_Results (Student_ID, Examiner_ID, Vehicle_ID, Exam_Date, Exam_Type, Grade) 
VALUES (13, 1, 2, '2023-04-15', 'Практический', 'Прошел');

-- Удаление студента по идентификатору

DELETE FROM Students
WHERE Student_ID = 1;

-- Удаление всех записей из таблицы "Студенты" (Students)
DELETE FROM Students;

-- запрос на информацию о студенте, включая название машины и имя фамилию инструктора

SELECT
    Students.Student_ID AS Student_ID,
    Students.First_Name AS Student_First_Name,
    Students.Last_Name AS Student_Last_Name,
    Students.Date_of_Birth AS Student_Date_of_Birth,
    Students.Address AS Student_Address,
    Students.Phone AS Student_Phone,
    Students.Email AS Student_Email,
    Students.Enrollment_Date AS Student_Enrollment_Date,
    Students.Graduation_Date AS Student_Graduation_Date,
    Vehicles.Make AS Vehicle_Make,
    Instructors.First_Name AS Instructor_First_Name,
    Instructors.Last_Name AS Instructor_Last_Name
FROM
    Students
INNER JOIN
    Schedule ON Students.Student_ID = Schedule.Student_ID
INNER JOIN
    Instructors ON Schedule.Instructor_ID = Instructors.Instructor_ID
INNER JOIN
    Vehicles ON Schedule.Vehicle_ID = Vehicles.Vehicle_ID
WHERE
    Students.First_Name = 'Иван' AND Students.Last_Name = 'Иванов' LIMIT 0,100
