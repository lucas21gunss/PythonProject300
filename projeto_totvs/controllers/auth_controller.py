# controllers/auth_controller.py
import jwt
import datetime
import logging
from functools import wraps
from flask import request, jsonify, current_app, g
from models.auth_model import AuthModel

logger = logging.getLogger("Auth")


class AuthController:
    def __init__(self):
        self.model = AuthModel()

    def login(self, username, password):
        # 1. Autentica no Protheus
        resultado = self.model.autenticar_protheus(username, password)

        if not resultado["success"]:
            logger.warning(f"Falha no login para {username}: {resultado.get('error')}")
            return resultado

        # 2. Gera JWT e guarda o token do Protheus dentro dele
        try:
            token_flask = jwt.encode(
                {
                    "user": username,
                    "protheus_token": resultado["access_token"],  # Token salvo aqui
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256",
            )

            return {"success": True, "token": token_flask, "user": username}
        except Exception as e:
            logger.error(f"Erro JWT: {e}")
            return {"success": False, "error": "Erro sessão"}


# Decorator atualizado
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split()[1]
        elif request.cookies.get("token"):
            token = request.cookies.get("token")

        if not token:
            return jsonify({"message": "Sessão inválida"}), 401

        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            g.user = data["user"]
            # RECUPERA O TOKEN AQUI PARA O PROJETO_CONTROLLER USAR
            g.protheus_token = data.get("protheus_token")
        except:
            return jsonify({"message": "Sessão expirada"}), 401

        return f(*args, **kwargs)

    return decorated
