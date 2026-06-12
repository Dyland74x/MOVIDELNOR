import os
from dotenv import load_dotenv

load_dotenv()

#class Config:
 #   SECRET_KEY = os.environ.get('SECRET_KEY') or 'movidelnor2017*'
  #  SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://tics:movidelnor2017*@localhost/gestion_turnos'
   # SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SESSION_TYPE = 'filesystem'
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'movidelnor2017*'
    # Cambiamos localhost por 127.0.0.1
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://tics:movidelnor2017*@127.0.0.1/gestion_turnos'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'

    