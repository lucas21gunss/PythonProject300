# views/routes.py
# Rotas da aplicação COM endpoint de requisição

from flask import render_template, jsonify, request
from controllers.projeto_controller import ProjetoController
from datetime import datetime


def init_routes(app):
    controller = ProjetoController()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/projetos')
    def api_projetos():
        resultado = controller.listar_projetos()
        return jsonify(resultado['data']) if resultado['success'] else (jsonify({'error': resultado['error']}), 500)

    @app.route('/api/celulas/<projeto>/<revisao>')
    def api_celulas(projeto, revisao):
        resultado = controller.listar_celulas(projeto, revisao)
        return jsonify(resultado['data']) if resultado['success'] else (jsonify({'error': resultado['error']}), 500)

    @app.route('/api/produtos/<projeto>/<revisao>/<celula>')
    def api_produtos(projeto, revisao, celula):
        resultado = controller.listar_produtos(projeto, revisao, celula)
        return jsonify(resultado) if resultado['success'] else (jsonify({'error': resultado['error']}), 500)

    @app.route('/api/requisicao', methods=['POST'])
    def api_requisicao():
        """
        Endpoint para receber requisição de produtos

        Body esperado:
        {
            "itens": [
                {
                    "codigo": "PROD001",
                    "descricao": "Parafuso",
                    "quantidade": 100,
                    "projeto": "PROJ001",
                    "celula": "CEL001"
                }
            ]
        }
        """
        try:
            dados = request.get_json()

            if not dados or 'itens' not in dados:
                return jsonify({'success': False, 'error': 'Dados inválidos'}), 400

            itens = dados['itens']

            if not itens or len(itens) == 0:
                return jsonify({'success': False, 'error': 'Nenhum item na requisição'}), 400

            # Validar dados
            for item in itens:
                if not all(k in item for k in ['codigo', 'quantidade', 'projeto', 'celula']):
                    return jsonify({'success': False, 'error': 'Item com dados incompletos'}), 400

                if item['quantidade'] <= 0:
                    return jsonify({'success': False, 'error': f"Quantidade inválida para {item['codigo']}"}), 400

            # AQUI VOCÊ PODE:
            # 1. Salvar no banco de dados
            # 2. Enviar para API externa
            # 3. Gerar PDF/Excel
            # 4. Enviar email
            # 5. Integrar com ERP

            # Exemplo: Log da requisição
            requisicao_id = f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            print("=" * 80)
            print(f"NOVA REQUISIÇÃO RECEBIDA: {requisicao_id}")
            print("=" * 80)
            for idx, item in enumerate(itens, 1):
                print(f"{idx}. {item['codigo']} - {item['descricao']} - Qtd: {item['quantidade']}")
                print(f"   Projeto: {item['projeto']} | Célula: {item['celula']}")
            print("=" * 80)

            # Retornar sucesso
            return jsonify({
                'success': True,
                'requisicao_id': requisicao_id,
                'total_itens': len(itens),
                'mensagem': 'Requisição processada com sucesso!'
            })

        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'TOTVS Projetos API'})