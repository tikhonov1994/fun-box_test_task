# **Тестовое задание в компанию Funbox**

## Инструкция по запуску
* Установите зависимости: `pip install -r requirements.txt`
* Запустите redis server
* Настройте данные для подключения к redis-server в файле `test_task/settings.py`
* Запустите сервер: `python manage.py runserver`


## Тестировние
###### Информация по тестированию: ![Build Status](https://github.com/tikhonov1994/fun-box_test_task/actions/workflows/tests.yml/badge.svg)
* Запустите команду: `python manage.py test api`