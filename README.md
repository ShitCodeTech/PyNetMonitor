Установка и настройка на локальном компьютере
Убедитесь, что на удаленном сервере установлен Python 3 и pip. Для этого введите в терминале следующие команды:

python3 --version
pip3 --version

Установите зависимости, выполнив команду:

pip install -r requirements.txt

Подготовка удалённого серверв
Создайте bash-скрипт на удаленном сервере с помощью любого текстового редактора, например nano и вставьте следующий код:

bash
Copy code
#!/bin/bash

if [ "$1" = "-r" ]; then
  echo "Rebooting..."
  shutdown -r now
elif [ "$1" = "-s" ]; then
  echo "Shutting down..."
  shutdown -h now
else
  echo "Invalid argument. Usage: $0 [-r | -s]"
  exit 1
fi
Сохраните скрипт в любую удобную директорию на удаленном сервере, например, в /usr/local/bin/.

Для того, чтобы присвоить bash скрипту выполнение от root без пароля, запустите команду visudo, которая открывает файл /etc/sudoers для редактирования. Добавьте следующую строку в конец файла:

username ALL=(root) NOPASSWD: /path/to/script.sh
Замените username на имя пользователя, от которого будет выполняться скрипт, /path/to/script.sh на путь к скрипту, который вы хотите выполнить от root без пароля.

Сохраните изменения и закройте редактор.

Использование: 
cd PyNetMonitor
python3 maim.py
close - Ctrl+C
