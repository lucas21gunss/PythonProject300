# app.py
# Arquivo principal da aplicação com configuração de LOGS

import logging
import os
from flask import Flask
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from views.routes import init_routes

# Garante que as variáveis de ambiente sejam carregadas no início
load_dotenv()

def configure_logging(app):
    """Configura o sistema de logs da aplicação"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("sistema.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    #logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info("=" * 60)
    app.logger.info("SISTEMA INICIADO - LOGS ATIVADOS")
    app.logger.info("=" * 60)


def create_app(config_name='development'):
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)

    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    configure_logging(app)
    init_routes(app)
    return app


if __name__ == '__main__':
    print("=" * 80)
    print("SISTEMA DE PROJETOS, CÉLULAS E PRODUTOS - TOTVS")
    print("=" * 80)

    app = create_app('development')

    print("🚀 Iniciando servidor...")
    print("📍 Acesse: http://localhost:5000")
    print("📝 Logs sendo gravados em: sistema.log")
    print("🔒 Variáveis de ambiente (.env) carregadas")
    print("=" * 80 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)