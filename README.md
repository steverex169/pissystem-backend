# nhs-neqas-django
 # Setup Django Project on Local Machine

The first thing to do is to clone the repository:

```sh
git clone https://github.com/labhazir/nhs-neqas-django.git
cd nhs-neqas-django
```

Copy settings_copy content into settings file:
```sh
copy nhs-neqas\settings_copy.py nhs-neqas\settings.py
```

Create a virtual environment to install dependencies in and activate it:
```sh
python -m venv env
env\Scripts\activate
```

Then install the dependencies:
```sh
pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment.

Once `pip` has finished downloading the dependencies:
```sh
python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`.

In order to setup database:
- Create database on PostgreSQL
- Replace NAME with the database name you just created
- Replace PASSWORD with your PostgreSQL password that you have setup during PostgreSQL installation

```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'YOURDATABASENAME',
        'USER': 'postgres',
        'PASSWORD': 'YOURPOSTGRESQLPASSWORD',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

Now, you can run migration commands:
```sh
python manage.py makemigrations
python manage.py migrate
```

