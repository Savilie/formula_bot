#!/bin/bash

## Функция для проверки подключения к MySQL
#wait_for_mysql() {
#    echo "Проверяем подключение к MySQL ($DB_HOST:$DB_PORT)..."
#    while ! python -c "
#import socket, sys
#try:
#    sock = socket.create_connection(('$DB_HOST', $DB_PORT), timeout=2)
#    sock.close()
#    sys.exit(0)
#except Exception:
#    sys.exit(1)
#"; do
#        echo "Ожидание MySQL..."
#        sleep 2
#    done
#    echo "MySQL подключен!"
#}
#
## Проверяем подключение к MySQL
#wait_for_mysql

# Инициализируем базу данных
python -c "from bot.database import init_db; init_db()"

# Запускаем бота
exec python -m main