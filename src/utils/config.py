import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


DEBUG = os.getenv('DEBUG', 'False') in ['True', 'true']
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')

JOBINDSATS_POSTGRES_DB_HOST = os.getenv("JOBINDSATS_POSTGRES_DB_HOST")
JOBINDSATS_POSTGRES_DB_USER = os.getenv("JOBINDSATS_POSTGRES_DB_USER")
JOBINDSATS_POSTGRES_DB_PASS = os.getenv("JOBINDSATS_POSTGRES_DB_PASS")
JOBINDSATS_POSTGRES_DB_DATABASE = os.getenv("JOBINDSATS_POSTGRES_DB_DATABASE")
JOBINDSATS_POSTGRES_DB_PORT = os.getenv("JOBINDSATS_POSTGRES_DB_PORT")
