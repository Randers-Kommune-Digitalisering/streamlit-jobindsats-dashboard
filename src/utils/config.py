import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


DEBUG = os.getenv('DEBUG', 'False') in ['True', 'true']
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')

# Keycloack Auth
# KEYCLOAK_URL = os.environ["KEYCLOAK_URL"].strip()
# KEYCLOAK_REALM = os.environ["KEYCLOAK_REALM"].strip()
# KEYCLOAK_CLIENT_ID = os.environ["KEYCLOAK_CLIENT_ID"].strip()

# Database
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')
