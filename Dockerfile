# Используем официальный образ MySQL
FROM mysql:latest

# Установим переменные окружения для базы данных
ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=auto_school
ENV MYSQL_USER=auto_school_user
ENV MYSQL_PASSWORD=auto_school_password

# Откроем порт 3306 для внешнего подключения
EXPOSE 3306
