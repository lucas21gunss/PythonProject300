# views/routes.py
import logging
from flask import render_template, jsonify, request, redirect, make_response, g
from controllers.projeto_controller import ProjetoController
from controllers.auth_controller import AuthController, token_required

logger = logging.getLogger('Routes')


def init_routes(app):
    projeto_controller = ProjetoController()
    auth_controller = AuthController()

    # ========== ROTAS DE AUTENTICAÇÃO ==========

    @app.route('/login', methods=['GET'])
    def login_page():
        """Exibe a página de login"""
        return render_template('login.html')

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """Endpoint de autenticação"""
        dados = request.get_json()

        if not dados:
            return jsonify({'success': False, 'error': 'Dados inválidos'}), 400

        username = dados.get('username')
        password = dados.get('password')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Usuário e senha são obrigatórios'}), 400

        # Tenta autenticar no Protheus
        resultado = auth_controller.login(username, password)

        if resultado['success']:
            # Login bem-sucedido - retorna o token
            resposta = make_response(jsonify(resultado))
            resposta.set_cookie(
                'token',
                resultado['token'],
                httponly=True,
                secure=False,  # Mude para True em produção com HTTPS
                max_age=28800  # 8 horas
            )
            logger.info(f"Login bem-sucedido: {username}")
            return resposta
        else:
            # Falha na autenticação
            logger.warning(f"Falha no login: {username}")
            return jsonify(resultado), 401

    @app.route('/logout')
    def logout():
        """Faz logout e redireciona para login"""
        resposta = make_response(redirect('/login'))
        resposta.delete_cookie('token')
        logger.info("Usuário fez logout")
        return resposta

    # ========== ROTA PRINCIPAL ==========

    @app.route('/')
    def index():
        """Página principal - requer autenticação"""
        if not request.cookies.get('token'):
            return redirect('/login')
        return render_template('index.html')

    # ========== ROTAS DA API (PROTEGIDAS) ==========

    @app.route('/api/projetos')
    @token_required
    def api_projetos():
        """Lista todos os projetos disponíveis"""
        logger.info(f"Usuário {g.user} solicitou lista de projetos")
        resultado = projeto_controller.listar_projetos()

        if resultado['success']:
            return jsonify(resultado['data'])
        else:
            logger.error(f"Erro ao listar projetos: {resultado.get('error')}")
            return jsonify(resultado), 500

    @app.route('/api/celulas/<projeto>/<revisao>')
    @token_required
    def api_celulas(projeto, revisao):
        """Lista células de um projeto específico"""
        logger.info(f"Usuário {g.user} solicitou células do projeto {projeto} rev {revisao}")
        resultado = projeto_controller.listar_celulas(projeto, revisao)

        if resultado['success']:
            return jsonify(resultado['data'])
        else:
            logger.error(f"Erro ao listar células: {resultado.get('error')}")
            return jsonify(resultado), 500

    @app.route('/api/produtos/<projeto>/<revisao>/<celula>')
    @token_required
    def api_produtos(projeto, revisao, celula):
        """Lista produtos de uma célula específica"""
        logger.info(f"Usuário {g.user} solicitou produtos - Projeto: {projeto}, Célula: {celula}")
        resultado = projeto_controller.listar_produtos(projeto, revisao, celula)

        if resultado['success']:
            return jsonify(resultado)
        else:
            logger.error(f"Erro ao listar produtos: {resultado.get('error')}")
            return jsonify(resultado), 500

    # ========== ROTA DE ENVIO DE ORDEM (PRINCIPAL) ==========

    @app.route('/api/requisicao', methods=['POST'])
    @token_required
    def api_requisicao():
        """
        Envia ordem de separação para o Protheus

        Payload esperado:
        {
            "projeto": "PMS005125A",
            "celulas": [
                {
                    "celula": "CELROB005125H",
                    "itens": [
                        {"produto": "ELXX.0643.01.MP", "quantidade": 1}
                    ]
                }
            ]
        }
        """
        try:
            dados = request.get_json()

            if not dados:
                logger.error("Requisição sem dados JSON")
                return jsonify({
                    'success': False,
                    'error': 'Dados não fornecidos'
                }), 400

            # Validações básicas
            if 'projeto' not in dados:
                logger.error("Campo 'projeto' ausente no payload")
                return jsonify({
                    'success': False,
                    'error': 'Campo "projeto" é obrigatório'
                }), 400

            if 'celulas' not in dados or not isinstance(dados['celulas'], list):
                logger.error("Campo 'celulas' ausente ou inválido no payload")
                return jsonify({
                    'success': False,
                    'error': 'Campo "celulas" deve ser uma lista'
                }), 400

            if len(dados['celulas']) == 0:
                logger.error("Lista de células vazia")
                return jsonify({
                    'success': False,
                    'error': 'Pelo menos uma célula deve ser informada'
                }), 400

            # Valida estrutura de cada célula
            for idx, celula in enumerate(dados['celulas']):
                if 'celula' not in celula or 'itens' not in celula:
                    logger.error(f"Célula {idx} com estrutura inválida")
                    return jsonify({
                        'success': False,
                        'error': f'Célula {idx} está com estrutura inválida'
                    }), 400

                if not isinstance(celula['itens'], list) or len(celula['itens']) == 0:
                    logger.error(f"Célula {celula['celula']} sem itens")
                    return jsonify({
                        'success': False,
                        'error': f'Célula {celula["celula"]} deve ter pelo menos um item'
                    }), 400

            # Log detalhado do que será enviado
            total_celulas = len(dados['celulas'])
            total_itens = sum(len(c['itens']) for c in dados['celulas'])

            logger.info(f"Usuário {g.user} enviando ordem de separação:")
            logger.info(f"  Projeto: {dados['projeto']}")
            logger.info(f"  Células: {total_celulas}")
            logger.info(f"  Total de itens: {total_itens}")

            # CHAMA O MÉTODO QUE FAZ A INTEGRAÇÃO REAL COM O PROTHEUS
            resultado = projeto_controller.enviar_ordem_separacao(dados)

            if resultado['success']:
                logger.info(f"✅ Ordem enviada com sucesso para o Protheus")
                logger.info(f"Resposta: {resultado.get('mensagem')}")
                return jsonify(resultado), 200
            else:
                logger.error(f"❌ Erro ao enviar ordem: {resultado.get('error')}")
                return jsonify(resultado), 400

        except ValueError as e:
            logger.exception("Erro de validação de dados")
            return jsonify({
                'success': False,
                'error': f'Dados inválidos: {str(e)}'
            }), 400

        except Exception as e:
            logger.exception("Erro inesperado ao processar requisição")
            return jsonify({
                'success': False,
                'error': f'Erro interno do servidor: {str(e)}'
            }), 500

    # ========== ROTA DE HEALTH CHECK ==========

    @app.route('/health')
    def health_check():
        """Verifica se o servidor está funcionando"""
        return jsonify({
            'status': 'ok',
            'service': 'Portal Manufatura MRB',
            'version': '2.0'
        })

    # ========== TRATAMENTO DE ERROS ==========

    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Rota não encontrada: {request.url}")
        return jsonify({
            'success': False,
            'error': 'Rota não encontrada'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erro interno do servidor: {error}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

    logger.info("Rotas configuradas com sucesso")