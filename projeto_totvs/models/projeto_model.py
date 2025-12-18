# models/projeto_model.py
# Model - SEM ORDER BY nas queries

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
        """Lista projetos SEM ORDER BY"""
        query = """
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
                  AND AF8_XCC = ' ' \
                """
        try:
            df = pd.read_sql(query, self.conn)
            return df.to_dict('records')
        except:
            return []

    def get_celulas(self, projeto, revisao):
        """Lista células SEM ORDER BY"""
        query = """
                SELECT AF8_PROJET, \
                       AF8_REVISA, \
                       AFC_XPROD,
                       SUM(AFA_QUANT)             AS AFA_QUANT,
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
                GROUP BY AF8_PROJET, AF8_REVISA, AFC_XPROD \
                """
        try:
            df = pd.read_sql(query, self.conn, params=[projeto, revisao])
            return df.to_dict('records')
        except:
            return []

    def get_produtos(self, projeto, revisao, celula):
        """Lista produtos SEM ORDER BY"""
        query = """
                SELECT AF8_PROJET, \
                       AFC_XPROD, \
                       AFA_PRODUT, \
                       AFA_XDESCR,
                       SUM(AFA_QUANT)             AS AFA_QUANT,
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
                GROUP BY AF8_PROJET, AFC_XPROD, AFA_PRODUT, AFA_XDESCR \
                """
        try:
            df = pd.read_sql(query, self.conn, params=[projeto, revisao, celula])
            return df.to_dict('records')
        except:
            return []