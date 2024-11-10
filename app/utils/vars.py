import os

MYSQL_URL: str = os.getenv("MYSQL_URL") if os.getenv("MYSQL_URL") != None  else "mysql://admin_db:admin_db@0.0.0.0:3306/fastapi"