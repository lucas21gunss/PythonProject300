# config.py
import base64


class Config:
    SECRET_KEY = 'B7lP8ZqJcN3X9rT1K2sV4W5eY6fG0qF3'
    DEBUG = True

    # ⬇️ CONFIGURE ESTES VALORES ⬇️
    DB_SERVER = '172.22.8.25'  # IP do servidor SQL (ou '127.0.0.1' se local)
    DB_DATABASE = 'ZT8HTG_DEV'  # Nome do seu banco SQL Server
    DB_USERNAME = 'sa'
    DB_PASSWORD_BASE64 = 'TW90b0B6dDhodGdkYQ=='

    @staticmethod
    def get_db_password():
        return base64.b64decode(Config.DB_PASSWORD_BASE64).decode('utf-8')

    @staticmethod
    def get_connection_string():
        return (
            f'DRIVER={{SQL Server}};'
            f'SERVER={Config.DB_SERVER};'
            f'DATABASE={Config.DB_DATABASE};'
            f'UID={Config.DB_USERNAME};'
            f'PWD={Config.get_db_password()}'
        )

    # Email
    EMAIL_ADDRESS = 'senha.portal.mrb@motoman.com.br'
    EMAIL_PASSWORD = 'naofazdiferenca'
    SMTP_SERVER = '172.22.8.35'
    SMTP_PORT = 25

    # Protheus REST API
    URL_REST_PROTHEUS = 'http://172.22.8.25:4003/rest'
    CHAVE_COLETOR = 'Q8%pA2!kZzL7$wMEr3#vNgTb@CHAVE_COLETOR'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False