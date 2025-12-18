# controllers/auth_controller.py
import jwt
import datetime
import logging
from functools import wraps
from flask import request, jsonify, current_app, g
from models.auth_model import AuthModel

# Logger específico para autenticação
logger = logging.getLogger('Auth')


class AuthController:
    def __init__(self):
        self.model = AuthModel()

    def login(self, username, password):
        # Log da tentativa (sem mostrar senha, claro)
        client_ip = request.remote_addr
        logger.info(f"Tentativa de login: Usuário '{username}' [IP: {client_ip}]")

        # Chama o model para autenticar no Protheus
        resultado = self.model.autenticar_protheus(username, password)

        if not resultado['success']:
            logger.warning(f"Falha de login: Usuário '{username}' - Motivo: {resultado.get('error')}")
            return resultado

        # Se sucesso, gera um token JWT interno
        try:
            token_flask = jwt.encode({
                'user': username,
                'protheus_token': resultado['access_token'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            logger.info(f"Login SUCESSO: Usuário '{username}' autenticado [IP: {client_ip}]")

            return {
                'success': True,
                'token': token_flask,
                'user': username
            }
        except Exception as e:
            logger.error(f"Erro ao gerar token JWT para '{username}': {str(e)}")
            return {'success': False, 'error': 'Erro interno na geração de token'}


# Decorator para proteger rotas E LOGAR ACESSOS
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        client_ip = request.remote_addr

        # Tenta pegar do Header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if "Bearer " in auth_header:
                token = auth_header.split(" ")[1]

        # Tenta pegar de Cookie
        if not token:
            token = request.cookies.get('token')

        if not token:
            logger.warning(f"Acesso negado (Sem Token): {request.method} {request.path} [IP: {client_ip}]")
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Token de autenticação ausente!'}), 401
            return jsonify({'redirect': '/login'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']

            # Salva o usuário no contexto global do Flask (g) para usar nas rotas
            g.user = current_user

            # --- O PULO DO GATO: LOG DE AUDITORIA DE ACESSO ---
            logger.info(
                f"AUDITORIA - Usuário: {current_user} | Ação: {request.method} {request.path} | IP: {client_ip}")
            # --------------------------------------------------

        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expirado [IP: {client_ip}]")
            return jsonify({'message': 'Token expirado, faça login novamente.'}), 401
        except Exception as e:
            logger.warning(f"Token inválido: {str(e)} [IP: {client_ip}]")
            return jsonify({'message': 'Token inválido!'}), 401

        return f(*args, **kwargs)

    return decorated