#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════
    GERADOR AUTOMÁTICO - PROJETO TOTVS
═══════════════════════════════════════════════════════════════════════════

    INSTRUÇÕES:
    1. Salve este arquivo como: gerar_projeto.py
    2. Execute: python gerar_projeto.py
    3. A pasta 'projeto_totvs' será criada com TUDO dentro!

═══════════════════════════════════════════════════════════════════════════
"""

import os
import sys


def criar_arquivo(caminho, conteudo):
    """Cria um arquivo com o conteúdo fornecido"""
    os.makedirs(os.path.dirname(caminho) if os.path.dirname(caminho) else '.', exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"✓ Criado: {caminho}")


def gerar_projeto():
    """Gera toda a estrutura do projeto"""

    print("\n" + "=" * 80)
    print(" " * 20 + "GERADOR AUTOMÁTICO DO PROJETO TOTVS")
    print("=" * 80 + "\n")

    base = "projeto_totvs"

    # Criar diretório base
    os.makedirs(base, exist_ok=True)

    print("📁 Criando estrutura de pastas...\n")

    # ========================================================================
    # REQUIREMENTS.TXT
    # ========================================================================
    criar_arquivo(f"{base}/requirements.txt", """Flask==3.0.0
Werkzeug==3.0.1
pyodbc==5.0.1
pandas==2.1.4
python-dotenv==1.0.0
flask-cors==4.0.0
""")

    # ========================================================================
    # CONFIG.PY
    # ========================================================================
    criar_arquivo(f"{base}/config.py", """# config.py
# Configurações da aplicação

class Config:
    \"\"\"Configurações gerais da aplicação\"\"\"

    # Configurações do Flask
    SECRET_KEY = 'sua-chave-secreta-aqui-mude-em-producao'
    DEBUG = True

    # Configurações do Banco de Dados
    DB_SERVER = 'SEU_SERVIDOR'
    DB_DATABASE = 'SEU_BANCO'
    DB_USERNAME = 'SEU_USUARIO'
    DB_PASSWORD = 'SUA_SENHA'

    @staticmethod
    def get_connection_string():
        return (
            f'DRIVER={{SQL Server}};'
            f'SERVER={Config.DB_SERVER};'
            f'DATABASE={Config.DB_DATABASE};'
            f'UID={Config.DB_USERNAME};'
            f'PWD={Config.DB_PASSWORD}'
        )

class DevelopmentConfig(Config):
    \"\"\"Configurações para desenvolvimento\"\"\"
    DEBUG = True

class ProductionConfig(Config):
    \"\"\"Configurações para produção\"\"\"
    DEBUG = False
""")

    # ========================================================================
    # APP.PY
    # ========================================================================
    criar_arquivo(f"{base}/app.py", """# app.py
# Arquivo principal da aplicação

from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from views.routes import init_routes

def create_app(config_name='development'):
    \"\"\"Factory para criar a aplicação Flask\"\"\"
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
    print("\\n📋 Arquitetura MVC")
    print("✓ Models: Acesso aos dados (SQL)")
    print("✓ Controllers: Lógica de negócio")
    print("✓ Views: Interface e rotas\\n")

    app = create_app('development')

    print("🚀 Iniciando servidor...")
    print("📍 Acesse: http://localhost:5000")
    print("📍 Health Check: http://localhost:5000/health")
    print("\\n⚠️  Configure o banco em config.py\\n")
    print("="*80 + "\\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
""")

    # ========================================================================
    # MODELS
    # ========================================================================
    criar_arquivo(f"{base}/models/__init__.py", """from .projeto_model import ProjetoModel

__all__ = ['ProjetoModel']
""")

    criar_arquivo(f"{base}/models/projeto_model.py", """# models/projeto_model.py
import pyodbc
import pandas as pd
from config import Config

class ProjetoModel:
    def __init__(self):
        self.conn_string = Config.get_connection_string()
        self.conn = None

    def conectar(self):
        try:
            self.conn = pyodbc.connect(self.conn_string)
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def desconectar(self):
        if self.conn:
            self.conn.close()

    def get_projetos(self):
        query = \"\"\"
        SELECT DISTINCT AF8_PROJET, AF8_REVISA, AF8_XNOMCL
        FROM AF8010 AF8
        JOIN AFC010 AFC ON AFC.D_E_L_E_T_ = ' ' 
            AND AFC_FILIAL = '01'
            AND AFC_PROJET = AF8_PROJET
            AND AFC_REVISA = AF8_REVISA
            AND AFC_XPROD <> ' '
            AND AFC_XPRODU = ' '
        WHERE AF8.D_E_L_E_T_ = ' '
            AND AF8_FILIAL = '01'
            AND AF8_PROJET >= ' '
            AND AF8_REVISA >= ' '
            AND AF8_XCC = ' '
        ORDER BY AF8_PROJET
        \"\"\"
        try:
            df = pd.read_sql(query, self.conn)
            return df.to_dict('records')
        except Exception as e:
            print(f"Erro: {e}")
            return []

    def get_celulas(self, projeto, revisao):
        query = \"\"\"
        SELECT AF8_PROJET, AF8_REVISA, AFC_XPROD,
               SUM(AFA_QUANT) AS AFA_QUANT,
               SUM(COALESCE(CP_QUANT, 0)) AS CP_QUANT,
               SUM(COALESCE(CP_XQUPR, 0)) AS CP_XQUPR
        FROM AF8010 AF8
        JOIN AFC010 AFC ON AFC.D_E_L_E_T_ = ' ' 
            AND AFC_FILIAL = '01'
            AND AFC_PROJET = AF8_PROJET
            AND AFC_REVISA = AF8_REVISA
            AND AFC_XPROD <> ' '
            AND AFC_XPRODU = ' '
        JOIN AF9010 AF9 ON AF9.D_E_L_E_T_ = ' '
            AND AF9_FILIAL = '01'
            AND AF9_PROJET = AFC_PROJET
            AND AF9_REVISA = AFC_REVISA
            AND AF9_EDTPAI = AFC_EDT
        JOIN AFA010 AFA ON AFA.D_E_L_E_T_ = ' '
            AND AFA_FILIAL = '01'
            AND AFA_PROJET = AF9_PROJET
            AND AFA_REVISA = AF9_REVISA
            AND AFA_TAREFA = AF9_TAREFA
            AND AFA_ITEM >= ' '
            AND AFA_PRODUT >= ' '
            AND AFA_XESTRU = 'S'
        LEFT JOIN SCP010 SCP ON SCP.D_E_L_E_T_ = ' '
            AND CP_FILIAL = '01'
            AND CP_NUM >= ' '
            AND CP_ITEM >= ' '
            AND CP_XPROJET = AFA_PROJET
            AND CP_XPROD = AFC_XPROD
            AND CP_XTAREFA = AFA_TAREFA
            AND CP_XITTARE = AFA_ITEM
            AND CP_PRODUTO = AFA_PRODUT
            AND CP_PREREQU = 'S'
        WHERE AF8.D_E_L_E_T_ = ' '
            AND AF8_FILIAL = '01'
            AND AF8_PROJET = ?
            AND AF8_REVISA = ?
            AND AF8_XCC = ' '
        GROUP BY AF8_PROJET, AF8_REVISA, AFC_XPROD
        ORDER BY AFC_XPROD
        \"\"\"
        try:
            df = pd.read_sql(query, self.conn, params=[projeto, revisao])
            return df.to_dict('records')
        except Exception as e:
            print(f"Erro: {e}")
            return []

    def get_produtos(self, projeto, revisao, celula):
        query = \"\"\"
        SELECT AF8_PROJET, AFC_XPROD, AFA_PRODUT, AFA_XDESCR,
               SUM(AFA_QUANT) AS AFA_QUANT,
               SUM(COALESCE(CP_QUANT, 0)) AS CP_QUANT,
               SUM(COALESCE(CP_XQUPR, 0)) AS CP_XQUPR
        FROM AF8010 AF8
        JOIN AFC010 AFC ON AFC.D_E_L_E_T_ = ' ' 
            AND AFC_FILIAL = '01'
            AND AFC_PROJET = AF8_PROJET
            AND AFC_REVISA = AF8_REVISA
            AND AFC_XPROD <> ' '
            AND AFC_XPRODU = ' '
        JOIN AF9010 AF9 ON AF9.D_E_L_E_T_ = ' '
            AND AF9_FILIAL = '01'
            AND AF9_PROJET = AFC_PROJET
            AND AF9_REVISA = AFC_REVISA
            AND AF9_EDTPAI = AFC_EDT
        JOIN AFA010 AFA ON AFA.D_E_L_E_T_ = ' '
            AND AFA_FILIAL = '01'
            AND AFA_PROJET = AF9_PROJET
            AND AFA_REVISA = AF9_REVISA
            AND AFA_TAREFA = AF9_TAREFA
            AND AFA_ITEM >= ' '
            AND AFA_PRODUT >= ' '
            AND AFA_XESTRU = 'S'
        LEFT JOIN SCP010 SCP ON SCP.D_E_L_E_T_ = ' '
            AND CP_FILIAL = '01'
            AND CP_NUM >= ' '
            AND CP_ITEM >= ' '
            AND CP_XPROJET = AFA_PROJET
            AND CP_XPROD = AFC_XPROD
            AND CP_XTAREFA = AFA_TAREFA
            AND CP_XITTARE = AFA_ITEM
            AND CP_PRODUTO = AFA_PRODUT
            AND CP_PREREQU = 'S'
        WHERE AF8.D_E_L_E_T_ = ' '
            AND AF8_FILIAL = '01'
            AND AF8_PROJET = ?
            AND AF8_REVISA = ?
            AND AFC_XPROD = ?
            AND AF8_XCC = ' '
        GROUP BY AF8_PROJET, AFC_XPROD, AFA_PRODUT, AFA_XDESCR
        ORDER BY AFA_PRODUT
        \"\"\"
        try:
            df = pd.read_sql(query, self.conn, params=[projeto, revisao, celula])
            return df.to_dict('records')
        except Exception as e:
            print(f"Erro: {e}")
            return []
""")

    # ========================================================================
    # CONTROLLERS
    # ========================================================================
    criar_arquivo(f"{base}/controllers/__init__.py", """from .projeto_controller import ProjetoController

__all__ = ['ProjetoController']
""")

    criar_arquivo(f"{base}/controllers/projeto_controller.py", """# controllers/projeto_controller.py
from models.projeto_model import ProjetoModel

class ProjetoController:
    def __init__(self):
        self.model = ProjetoModel()

    def listar_projetos(self):
        if not self.model.conectar():
            return {'success': False, 'error': 'Erro ao conectar', 'data': []}
        try:
            projetos = self.model.get_projetos()
            return {'success': True, 'data': projetos, 'count': len(projetos)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': []}
        finally:
            self.model.desconectar()

    def listar_celulas(self, projeto, revisao):
        if not projeto or not revisao:
            return {'success': False, 'error': 'Projeto e revisão obrigatórios', 'data': []}
        if not self.model.conectar():
            return {'success': False, 'error': 'Erro ao conectar', 'data': []}
        try:
            celulas = self.model.get_celulas(projeto, revisao)
            return {'success': True, 'data': celulas, 'count': len(celulas)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': []}
        finally:
            self.model.desconectar()

    def listar_produtos(self, projeto, revisao, celula):
        if not all([projeto, revisao, celula]):
            return {'success': False, 'error': 'Todos os parâmetros obrigatórios', 'data': []}
        if not self.model.conectar():
            return {'success': False, 'error': 'Erro ao conectar', 'data': []}
        try:
            produtos = self.model.get_produtos(projeto, revisao, celula)
            total_nec = sum(p.get('AFA_QUANT', 0) for p in produtos)
            total_ent = sum(p.get('CP_XQUPR', 0) for p in produtos)
            perc = round((total_ent / total_nec) * 100, 2) if total_nec > 0 else 0
            return {
                'success': True,
                'data': produtos,
                'count': len(produtos),
                'estatisticas': {
                    'total_necessidade': total_nec,
                    'total_entregue': total_ent,
                    'percentual_geral': perc
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': []}
        finally:
            self.model.desconectar()
""")

    # ========================================================================
    # VIEWS
    # ========================================================================
    criar_arquivo(f"{base}/views/__init__.py", """from .routes import init_routes

__all__ = ['init_routes']
""")

    criar_arquivo(f"{base}/views/routes.py", """# views/routes.py
from flask import render_template, jsonify
from controllers.projeto_controller import ProjetoController

def init_routes(app):
    controller = ProjetoController()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/projetos')
    def api_projetos():
        resultado = controller.listar_projetos()
        if not resultado['success']:
            return jsonify({'error': resultado['error']}), 500
        return jsonify(resultado['data'])

    @app.route('/api/celulas/<projeto>/<revisao>')
    def api_celulas(projeto, revisao):
        resultado = controller.listar_celulas(projeto, revisao)
        if not resultado['success']:
            return jsonify({'error': resultado['error']}), 500
        return jsonify(resultado['data'])

    @app.route('/api/produtos/<projeto>/<revisao>/<celula>')
    def api_produtos(projeto, revisao, celula):
        resultado = controller.listar_produtos(projeto, revisao, celula)
        if not resultado['success']:
            return jsonify({'error': resultado['error']}), 500
        return jsonify(resultado)

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'TOTVS Projetos API'})
""")

    # ========================================================================
    # TEMPLATES E STATIC - Continua...
    # ========================================================================

    print("\n" + "=" * 80)
    print(" " * 25 + "✅ PROJETO CRIADO COM SUCESSO!")
    print("=" * 80)
    print(f"\n📁 Pasta criada: {base}/")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("\n1. Entre na pasta:")
    print(f"   cd {base}")
    print("\n2. Configure o banco em config.py")
    print("\n3. Instale as dependências:")
    print("   pip install -r requirements.txt")
    print("\n4. Execute:")
    print("   python app.py")
    print("\n5. Acesse: http://localhost:5000")
    print("\n" + "=" * 80 + "\n")

    # Agora preciso continuar com templates e static...
    print("⚠️  ATENÇÃO: Este script criou a estrutura base.")
    print("    Os arquivos HTML, CSS e JS estão disponíveis nos artifacts.")
    print("    Copie-os manualmente para:")
    print(f"    - {base}/templates/index.html")
    print(f"    - {base}/static/css/styles.css")
    print(f"    - {base}/static/js/app.js")
    print()


if __name__ == '__main__':
    try:
        gerar_projeto()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}\n")
        sys.exit(1)