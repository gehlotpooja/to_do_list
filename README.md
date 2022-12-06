# to_do_list

## A Basic To-Do Web Application using Django Framework

## Features
- User Authentication - Users can register, login, logout and reset password.
- Add, Edit, Mark tasks as Complete/Incomplete and Delete Tasks.
- Created API End points to get the User Data and User Tasks.

## Steps to be followed for first time use
- Run these commands - This will create your Tables (by the Model definition) in the Database
```
python manage.py migrate

python manage.py makemigrations

python manage.py migrate
```
- Create an admin user by running these following commands
```
python manage.py createsuperuser
```

- To run server use below command (127.0.0.1:9000 is configured to send password on CLI, in case you want to change it to some other port and host then make these changes in setting.py under to_do_list folder)
```
python manage.py runserver 127.0.0.1:9000
```
