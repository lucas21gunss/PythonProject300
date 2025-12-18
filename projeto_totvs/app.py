# app.py
# Arquivo principal da aplicação

from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from views.routes import init_routes

def create_app(config_name='development'):
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)

    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    init_routes(app)
    return app

if __name__ == '__main__':
    print("="*80)
    print("SISTEMA DE PROJETOS, CÉLULAS E PRODUTOS - TOTVS")
    print("="*80)
    print("\n📋 Arquitetura MVC")
    print("✓ Models: Acesso aos dados (SQL)")
    print("✓ Controllers: Lógica de negócio")
    print("✓ Views: Interface e rotas\n")

    app = create_app('development')

    print("🚀 Iniciando servidor...")
    print("📍 Acesse: http://localhost:5000")
    print("📍 Health Check: http://localhost:5000/health")
    print("\n⚠️  Configure o banco em config.py\n")
    print("="*80 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
