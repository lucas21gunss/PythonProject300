# config.py
import os
import base64
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """Configuração base da aplicação"""

    # ========== SEGURANÇA ==========
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'chave-padrao-dev-nao-usar-em-producao')
    DEBUG = True

    # ========== BANCO DE DADOS (SQL SERVER) ==========
    DB_SERVER = os.getenv('DB_SERVER', '172.22.8.25')
    DB_DATABASE = os.getenv('DB_DATABASE', 'ZT8HTG_DEV')
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD_BASE64 = os.getenv('DB_PASSWORD_BASE64')

    @staticmethod
    def get_db_password():
        """Decodifica a senha do banco que está em Base64"""
        try:
            if not Config.DB_PASSWORD_BASE64:
                return ""
            decoded = base64.b64decode(Config.DB_PASSWORD_BASE64).decode('utf-8')
            return decoded
        except Exception as e:
            print(f"Erro ao decodificar senha do banco: {e}")
            return ""

    @staticmethod
    def get_connection_string():
        """Retorna a string de conexão do SQL Server"""
        return (
            f'DRIVER={{SQL Server}};'
            f'SERVER={Config.DB_SERVER};'
            f'DATABASE={Config.DB_DATABASE};'
            f'UID={Config.DB_USERNAME};'
            f'PWD={Config.get_db_password()}'
        )

    # ========== CONFIGURAÇÕES DE EMAIL ==========
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'senha.portal.mrb@motoman.com.br')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SMTP_SERVER = os.getenv('SMTP_SERVER', '172.22.8.35')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 25))

    # ========== INTEGRAÇÃO COM PROTHEUS ==========
    # URL base do REST do Protheus (sem a barra final)
    URL_REST_PROTHEUS = os.getenv('URL_REST_PROTHEUS', 'http://172.22.8.25:4003/rest/')

    # Endpoint específico para ordem de separação
    ENDPOINT_ORDEM_SEPARACAO = '/mmacdw02/ordem_separacao_fabrica/'

    # Chave do coletor (se necessário)
    CHAVE_COLETOR = os.getenv('CHAVE_COLETOR')

    @staticmethod
    def get_url_ordem_separacao():
        """Retorna a URL completa para o endpoint de ordem de separação"""
        base = Config.URL_REST_PROTHEUS.rstrip('/')
        endpoint = Config.ENDPOINT_ORDEM_SEPARACAO
        return f"{base}{endpoint}"

    # ========== TIMEOUTS E LIMITES ==========
    REQUEST_TIMEOUT = 60  # segundos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # ========== LOGGING ==========
    LOG_FILE = 'sistema.log'
    LOG_LEVEL = 'INFO'


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False
    TESTING = False

    # Em produção, certifique-se de ter uma SECRET_KEY forte
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

    if not SECRET_KEY:
        raise ValueError("FLASK_SECRET_KEY deve ser definida em produção!")


class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DEBUG = True


# Dicionário para facilitar a seleção do ambiente
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='development'):
    """Retorna a configuração apropriada baseada no nome do ambiente"""
    return config_by_name.get(config_name, DevelopmentConfig)