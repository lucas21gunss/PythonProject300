# views/routes.py
# Rotas da aplicação COM autenticação e LOGS DETALHADOS

import logging
from flask import render_template, jsonify, request, redirect, make_response, g
from controllers.projeto_controller import ProjetoController
from controllers.auth_controller import AuthController, token_required
from datetime import datetime

# Logger específico para as rotas/negócio
logger = logging.getLogger('Routes')


def init_routes(app):
    projeto_controller = ProjetoController()
    auth_controller = AuthController()

    # --- ROTAS DE AUTENTICAÇÃO ---

    @app.route('/login', methods=['GET'])
    def login_page():
        return render_template('login.html')

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        dados = request.get_json()

        if not dados or not dados.get('username') or not dados.get('password'):
            return jsonify({'success': False, 'error': 'Usuário e senha obrigatórios'}), 400

        resultado = auth_controller.login(dados['username'], dados['password'])

        if resultado['success']:
            resp = make_response(jsonify(resultado))
            # Cookie válido por 8 horas
            resp.set_cookie('token', resultado['token'], httponly=False, max_age=28800)
            return resp
        else:
            return jsonify(resultado), 401

    @app.route('/logout')
    def logout():
        resp = make_response(redirect('/login'))
        resp.delete_cookie('token')
        return resp

    # --- ROTAS DA APLICAÇÃO (PROTEGIDAS) ---

    @app.route('/')
    def index():
        token = request.cookies.get('token')
        if not token:
            return redirect('/login')
        return render_template('index.html')

    @app.route('/api/projetos')
    @token_required
    def api_projetos():
        # O log de acesso já é feito automaticamente pelo @token_required
        resultado = projeto_controller.listar_projetos()

        if not resultado['success']:
            logger.error(f"Erro listando projetos para {g.user}: {resultado['error']}")
            return jsonify({'error': resultado['error']}), 500

        return jsonify(resultado['data'])

    @app.route('/api/celulas/<projeto>/<revisao>')
    @token_required
    def api_celulas(projeto, revisao):
        resultado = projeto_controller.listar_celulas(projeto, revisao)

        if not resultado['success']:
            logger.error(f"Erro listando células ({projeto}) para {g.user}: {resultado['error']}")
            return jsonify({'error': resultado['error']}), 500

        return jsonify(resultado['data'])

    @app.route('/api/produtos/<projeto>/<revisao>/<celula>')
    @token_required
    def api_produtos(projeto, revisao, celula):
        resultado = projeto_controller.listar_produtos(projeto, revisao, celula)

        if not resultado['success']:
            logger.error(f"Erro listando produtos ({celula}) para {g.user}: {resultado['error']}")
            return jsonify({'error': resultado['error']}), 500

        return jsonify(resultado)

    @app.route('/api/requisicao', methods=['POST'])
    @token_required
    def api_requisicao():
        """
        Endpoint de Requisição com Log Detalhado da Operação
        """
        try:
            dados = request.get_json()
            user_logado = g.user  # Recuperado pelo token_required

            if not dados or 'itens' not in dados:
                logger.warning(f"Requisição inválida tentada por {user_logado}: Dados incompletos")
                return jsonify({'success': False, 'error': 'Dados inválidos'}), 400

            itens = dados['itens']

            if not itens or len(itens) == 0:
                return jsonify({'success': False, 'error': 'Nenhum item na requisição'}), 400

            # Validar dados
            for item in itens:
                if not all(k in item for k in ['codigo', 'quantidade', 'projeto', 'celula']):
                    return jsonify({'success': False, 'error': 'Item com dados incompletos'}), 400
                if item['quantidade'] <= 0:
                    return jsonify({'success': False, 'error': f"Qtd inválida para {item['codigo']}"}), 400

            # Identificador único da transação
            requisicao_id = f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # --- LOG DE AUDITORIA DE NEGÓCIO ---
            logger.info(f"⚡ NOVA REQUISIÇÃO [{requisicao_id}] - Usuário: {user_logado}")
            for idx, item in enumerate(itens, 1):
                logger.info(f"   Item {idx}: {item['codigo']} (Qtd: {item['quantidade']}) - Cel: {item['celula']}")
            # ------------------------------------

            # Print no console para debug rápido
            print("=" * 80)
            print(f"NOVA REQUISIÇÃO: {requisicao_id} | USUÁRIO: {user_logado}")
            print("=" * 80)

            return jsonify({
                'success': True,
                'requisicao_id': requisicao_id,
                'total_itens': len(itens),
                'mensagem': 'Requisição processada com sucesso!'
            })

        except Exception as e:
            logger.critical(f"Erro CRÍTICO processando requisição de {g.user}: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'TOTVS Projetos API'})