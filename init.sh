#!/bin/bash

user=admin
email=admin@admin.com
password=admin

python tayle/manage.py migrate

echo "from django.contrib.auth import get_user_model;
try:
  get_user_model().objects.create_superuser('$user', '$email', '$password')
except:
  print('Пользователь $user создан')" |
python tayle/manage.py shell
