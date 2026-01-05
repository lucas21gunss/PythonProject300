# controllers/projeto_controller.py
from models.projeto_model import ProjetoModel
from flask import g
import requests
import json
import logging
from config import Config

logger = logging.getLogger("ProtheusIntegration")


class ProjetoController:
    def __init__(self):
        self.model = ProjetoModel()

    # --- LEITURAS (MANTIDAS IGUAIS) ---
    def listar_projetos(self):
        if not self.model.conectar():
            return {"success": False, "error": "Erro Banco"}
        try:
            return {"success": True, "data": self.model.get_projetos()}
        finally:
            self.model.desconectar()

    def listar_celulas(self, projeto, revisao):
        if not self.model.conectar():
            return {"success": False, "error": "Erro Banco"}
        try:
            return {"success": True, "data": self.model.get_celulas(projeto, revisao)}
        finally:
            self.model.desconectar()

    def listar_produtos(self, projeto, revisao, celula):
        if not self.model.conectar():
            return {"success": False, "error": "Erro Banco"}
        try:
            dados = self.model.get_produtos(projeto, revisao, celula)
            total_nec = sum(d["AFA_QUANT"] for d in dados)
            total_ent = sum(d["CP_XQUPR"] for d in dados)
            perc = round((total_ent / total_nec * 100)) if total_nec > 0 else 0
            return {
                "success": True,
                "data": dados,
                "estatisticas": {
                    "total_necessidade": total_nec,
                    "total_entregue": total_ent,
                    "percentual_geral": perc,
                },
            }
        finally:
            self.model.desconectar()

    # --- ENVIO DE ORDEM (COM LIMPEZA DE ESPAÇOS) ---
    def enviar_ordem_separacao(self, payload):
        token_protheus = getattr(g, "protheus_token", None)

        if not token_protheus:
            return {"success": False, "error": "Sessão expirada. Faça login novamente."}

        try:
            # --- SANITIZAÇÃO (NOVO): Remove espaços em branco do payload ---
            # Ex: 'CELULA  ' vira 'CELULA'
            if payload.get("projeto"):
                payload["projeto"] = str(payload["projeto"]).strip()

            if payload.get("celulas"):
                for c in payload["celulas"]:
                    if c.get("celula"):
                        c["celula"] = str(c["celula"]).strip()

                    if c.get("itens"):
                        for item in c["itens"]:
                            if item.get("produto"):
                                item["produto"] = str(item["produto"]).strip()
            # -------------------------------------------------------------

            base_url = Config.URL_REST_PROTHEUS
            if base_url.endswith("/"):
                base_url = base_url[:-1]

            endpoint = "/mmacdw02/ordem_separacao_fabrica/"
            url_completa = f"{base_url}{endpoint}"

            headers = {
                "Authorization": f"Bearer {token_protheus}",
                "Content-Type": "application/json",
            }

            # Log para conferir se os espaços sumiram
            logger.info(f"POST {url_completa}")
            logger.info(f"Payload Limpo: {json.dumps(payload, ensure_ascii=False)}")

            response = requests.post(
                url_completa, json=payload, headers=headers, timeout=60, verify=False
            )

            # Tratamento da Resposta
            dados_retorno = None
            try:
                dados_retorno = response.json()
            except:
                dados_retorno = None

            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "mensagem": "Ordem processada com sucesso!",
                    "dados_protheus": dados_retorno,
                }

            elif response.status_code == 404:
                # Trata erro de negócio (quando o Protheus retorna 404 pq não achou itens)
                if dados_retorno:
                    msg_erro = "Protheus: Erro ao processar."
                    if "celulas" in dados_retorno and isinstance(
                        dados_retorno["celulas"], list
                    ):
                        msgs = [
                            c.get("mensagem")
                            for c in dados_retorno["celulas"]
                            if c.get("mensagem")
                        ]
                        if msgs:
                            msg_erro = f"Protheus: {'; '.join(msgs)}"
                    elif "mensagem" in dados_retorno:
                        msg_erro = dados_retorno["mensagem"]

                    return {"success": False, "error": msg_erro}
                else:
                    return {
                        "success": False,
                        "error": f"Serviço não encontrado (URL Errada).",
                    }

            else:
                msg = response.text
                if dados_retorno and "mensagem" in dados_retorno:
                    msg = dados_retorno["mensagem"]
                return {
                    "success": False,
                    "error": f"Erro Protheus ({response.status_code}): {msg}",
                }

        except Exception as e:
            logger.exception(f"Erro ao enviar: {e}")
            return {"success": False, "error": f"Erro interno: {str(e)}"}
