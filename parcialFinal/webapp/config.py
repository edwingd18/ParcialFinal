import os

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'db')
    MYSQL_USER = os.getenv('MYSQL_USER', 'user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'secret')
    MYSQL_DB = os.getenv('MYSQL_DATABASE', 'mydb')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

    # Construye la URI usando los valores anteriores
    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

