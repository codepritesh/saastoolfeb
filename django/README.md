# Setup server
+ install django channels(only one):
    - pip3 install django channels
    - pip3 install channels-redis
    - apt install redis-server 
    # follow document: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04

+ starting with new project(only one):
    # document: https://realpython.com/getting-started-with-django-channels
    - django-admin.py startproject <example_channels_project>

+ config in project(only one):
    # follow documents:
    > https://github.com/django/channels_redis
    > https://channels.readthedocs.io/en/latest/tutorial/part_1.html [option]

pip3 install flask flask_socketio ccxt pymongo python-binance flask-login gevent gunicorn asgiref websockets paramiko channels singleton_decorator channels_redis python-telegram-bot django channels channels-redis psycopg2-binary django-better-admin-arrayfield redis-server numpy rx uvicorn 
pip3 install ta

pip install django-redis

+ start new app and runserver:
    > python3 -m django --version
    > python3 manage.py runserver [0:<port>]
    > python3 manage.py startapp <new_app>
    > python3 manage.py migrate
    > python3 manage.py createsuperuser

+ Some document:
    > https://www.freecodecamp.org/news/using-django-with-mongodb-by-adding-just-one-line-of-code-c386a298e179/
    > https://docs.djangoproject.com/en/3.0/ref/templates/builtins/#std:templatetag-block
    > https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/

# Create db with postgreSQL
> install PostgreSQL
    sudo apt-get install postgresql postgresql-contrib libpq-dev
    pip3 install django psycopg2
> Use:
    > sudo su - postgres
    > psql
    > postgres=# CREATE DATABASE trading_bots;
    CREATE DATABASE
    > postgres=# CREATE USER admin1 WITH PASSWORD 'admin@123';
    CREATE ROLE
    > postgres=# ALTER ROLE admin SET client_encoding TO 'utf8';
    ALTER ROLE
    > postgres=# ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
    ALTER ROLE
    > postgres=# ALTER ROLE admin SET timezone TO 'UTC';
    > ALTER ROLE
    > postgres=# GRANT ALL PRIVILEGES ON DATABASE trading_bots TO admin;
    GRANT
    > postgres=# \q
> command:
    > \l list
    > \c choose database
    > \dt list table
    > SELECT * FROM <table>;

# Create USER DB with schema
##############################################
create table setup_apikey_apikey
(
    id          serial       not null
        constraint setup_apikey_apikey_pkey
            primary key,
    name        varchar(100) not null
        constraint setup_apikey_apikey_name_key
            unique,
    ex_id       varchar(3)   not null,
    api_keys    text         not null,
    secret_keys text         not null,
    passphrase  text         not null,
    own_name_id integer
        constraint setup_apikey_apikey_own_name_id_29770549_fk_auth_user_id
            references auth_user
            deferrable initially deferred,
    added_by    varchar(100) not null,
    exclude_pnl boolean      not null,
    tags        varchar(200)[]
);

alter table setup_apikey_apikey
    owner to postgres;

create index setup_apikey_apikey_name_4be5ed46_like
    on setup_apikey_apikey (name);

create index setup_apikey_apikey_user_id_id_98a07a7e
    on setup_apikey_apikey (own_name_id);
##############################################



# Create new app on Django
> python3 manage.py startapp denverbot
+ Add path/url to `d_trading_bots/urls.py`
+ Add application to `d_trading_bots/settings.py`
+ Add routing to `d_trading_bots/routing.py`
+ Create a new file in denverbot: `routing.py` and `consumer.py`
+ Change urls and view  of `denverbot/urls.py` and `denverbot/views.py`
+ Add file service `services/denver/denver_service.py` to call START/STOP bot
+ html/css/js: each bot need a FE was implemention in html,css,js.

++ Create super user
> python3 manage.py createsuperuser
++ If using model we need run 2 commands:
> python3 manage.py makemigrations <app>
> python3 manage.py migrate
++ Running server for testing
> python3 manage.py runserver 0:8001




___________________Mongodb_________________

db.createUser({ user:"myAdmin", pwd: "abc123321", roles: [{role: "userAdminAnyDatabase", db: "admin"}] })

___________________Mongodb_________________
