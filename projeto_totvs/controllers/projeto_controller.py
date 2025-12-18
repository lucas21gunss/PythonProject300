# controllers/projeto_controller.py
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
