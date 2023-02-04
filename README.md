# YATUBE_PROJECT
##### Cоциальная сеть Yatube, где реализованы следующие функции:
- просмотр всех постов
- создание поста
- комментирование постов
- создание подписок на других пользователей

## Стек технологий:
- Python
- Django
- HTML
- CSS

## Запуск проекта в dev-режиме
Клонировать репозиторий и перейти в него в командной строке:
``` 
git clone git@github.com:IgorKrupko-94/yatube_project.git 
```
``` 
cd yatube_project
```
Установите и активируйте виртуальное окружение c учётом версии Python 3.7 (выбираем python не ниже 3.7):
``` 
py -3.7 -m venv venv 
```
Для пользователей Windows:
``` 
source venv/Scripts/activate 
```
Для пользователей Linux и macOS:
``` 
source venv/bin/activate 
```
Обновляем до последней версии пакетный менеджер pip:
``` 
python -m pip install --upgrade pip 
```
Затем нужно установить все зависимости из файла requirements.txt:
``` 
pip install -r requirements.txt 
```
Выполняем миграции:
``` 
python manage.py makemigrations
python manage.py migrate 
```
Запускаем проект:
``` 
python manage.py runserver 
```
### Autor
Igor Krupko
