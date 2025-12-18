// static/js/app.js
// JavaScript da aplicação

// Estado global
let projetoSelecionado = null;
let celulaSelecionada = null;

// Atualizar data no header
function atualizarData() {
    const dataElement = document.getElementById('currentDate');
    if (dataElement) {
        const hoje = new Date();
        dataElement.textContent = hoje.toLocaleDateString('pt-BR');
    }
}

// Mostrar mensagem de erro
function mostrarErro(mensagem, containerId = 'mainContent') {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="error-message">
            ⚠️ ${mensagem}
        </div>
    `;
}

// Carregar projetos
async function carregarProjetos() {
    const lista = document.getElementById('projetosList');

    try {
        lista.innerHTML = '<li class="loading">Carregando projetos...</li>';

        const response = await fetch('/api/projetos');

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const projetos = await response.json();

        if (projetos.error) {
            throw new Error(projetos.error);
        }

        if (projetos.length === 0) {
            lista.innerHTML = `
                <li class="selection-item disabled">
                    <div style="text-align: center;">Nenhum projeto encontrado</div>
                </li>
            `;
            return;
        }

        lista.innerHTML = projetos.map(p => `
            <li class="selection-item" onclick="selecionarProjeto('${p.AF8_PROJET}', '${p.AF8_REVISA}', event)">
                <div class="selection-item-main">${p.AF8_PROJET}</div>
                <div class="selection-item-sub">${p.AF8_XNOMCL || 'Sem nome'}</div>
                <div class="selection-item-sub">Rev. ${p.AF8_REVISA}</div>
            </li>
        `).join('');

    } catch (error) {
        console.error('Erro ao carregar projetos:', error);
        lista.innerHTML = `
            <li class="selection-item disabled">
                <div style="text-align: center; color: red;">
                    Erro ao carregar projetos<br>
                    <small>${error.message}</small>
                </div>
            </li>
        `;
    }
}

// Selecionar projeto
async function selecionarProjeto(projeto, revisao, event) {
    projetoSelecionado = { projeto, revisao };
    celulaSelecionada = null;

    // Atualizar seleção visual
    document.querySelectorAll('#projetosList .selection-item').forEach(el => {
        el.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    // Carregar células
    const celulasList = document.getElementById('celulasList');
    celulasList.innerHTML = '<li class="loading">Carregando células...</li>';

    try {
        const response = await fetch(`/api/celulas/${projeto}/${revisao}`);

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const celulas = await response.json();

        if (celulas.error) {
            throw new Error(celulas.error);
        }

        if (celulas.length === 0) {
            celulasList.innerHTML = `
                <li class="selection-item disabled">
                    <div style="text-align: center;">Nenhuma célula disponível</div>
                </li>
            `;
        } else {
            celulasList.innerHTML = celulas.map(c => {
                const necessidade = c.AFA_QUANT || 0;
                const entregue = c.CP_XQUPR || 0;
                const percentual = necessidade > 0 ? Math.round((entregue / necessidade) * 100) : 0;

                return `
                    <li class="selection-item" onclick="selecionarCelula('${c.AFC_XPROD}', event)">
                        <div class="selection-item-main">${c.AFC_XPROD}</div>
                        <div class="selection-item-sub">Necessidade: ${necessidade}</div>
                        <div class="selection-item-sub">Entregue: ${entregue} (${percentual}%)</div>
                    </li>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Erro ao carregar células:', error);
        celulasList.innerHTML = `
            <li class="selection-item disabled">
                <div style="text-align: center; color: red;">
                    Erro ao carregar células<br>
                    <small>${error.message}</small>
                </div>
            </li>
        `;
    }

    // Atualizar conteúdo principal
    document.getElementById('mainTitle').textContent = `Produtos - ${projeto}`;
    document.getElementById('mainSubtitle').textContent = `Selecione uma célula`;
    document.getElementById('mainContent').innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">👇</div>
            <div class="empty-state-text">
                <p>Selecione uma célula para visualizar os produtos</p>
            </div>
        </div>
    `;
}

// Selecionar célula
async function selecionarCelula(celula, event) {
    celulaSelecionada = celula;

    // Atualizar seleção visual
    document.querySelectorAll('#celulasList .selection-item').forEach(el => {
        el.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    // Mostrar loading
    document.getElementById('mainContent').innerHTML = '<div class="loading">Carregando produtos...</div>';

    try {
        const response = await fetch(
            `/api/produtos/${projetoSelecionado.projeto}/${projetoSelecionado.revisao}/${celula}`
        );

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const resultado = await response.json();

        if (resultado.error) {
            throw new Error(resultado.error);
        }

        const produtos = resultado.data || [];
        const estatisticas = resultado.estatisticas || {};

        // Atualizar título
        document.getElementById('mainTitle').textContent =
            `Produtos - ${projetoSelecionado.projeto} / ${celula}`;
        document.getElementById('mainSubtitle').textContent = `Célula ${celula}`;

        // Verificar se há produtos
        if (produtos.length === 0) {
            document.getElementById('mainContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <div class="empty-state-text">
                        <p>Nenhum produto disponível para esta célula</p>
                    </div>
                </div>
            `;
            return;
        }

        // Gerar tabela
        const tabela = `
            <div class="breadcrumb">
                <strong>Projeto:</strong> ${projetoSelecionado.projeto} | 
                <strong>Célula:</strong> ${celula}
            </div>
            
            ${estatisticas.total_necessidade ? `
            <div class="stats-box">
                <div class="stat-item">
                    <div class="stat-label">Total Necessidade</div>
                    <div class="stat-value">${estatisticas.total_necessidade}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Entregue</div>
                    <div class="stat-value">${estatisticas.total_entregue}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Percentual</div>
                    <div class="stat-value">${estatisticas.percentual_geral}%</div>
                </div>
            </div>
            ` : ''}
            
            <div class="info-box">
                ℹ️ Total de ${produtos.length} produto(s) nesta célula
            </div>
            
            <table class="products-table">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Descrição</th>
                        <th class="quantity-cell">Necessidade</th>
                        <th class="quantity-cell">Reservado</th>
                        <th class="quantity-cell">Entregue</th>
                        <th class="quantity-cell">Pendente</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${produtos.map(prod => {
                        const necessidade = prod.AFA_QUANT || 0;
                        const reservado = prod.CP_QUANT || 0;
                        const entregue = prod.CP_XQUPR || 0;
                        const pendente = necessidade - entregue;
                        const percentual = necessidade > 0 ? 
                            Math.round((entregue / necessidade) * 100) : 0;
                        
                        let status = 'pending';
                        let statusText = 'Pendente';
                        
                        if (entregue >= necessidade && necessidade > 0) {
                            status = 'complete';
                            statusText = 'Completo';
                        } else if (entregue > 0) {
                            status = 'partial';
                            statusText = `Parcial (${percentual}%)`;
                        }
                        
                        return `
                            <tr>
                                <td><strong>${prod.AFA_PRODUT}</strong></td>
                                <td>${prod.AFA_XDESCR || 'Sem descrição'}</td>
                                <td class="quantity-cell">${necessidade}</td>
                                <td class="quantity-cell">${reservado}</td>
                                <td class="quantity-cell">${entregue}</td>
                                <td class="quantity-cell">${pendente}</td>
                                <td><span class="status-badge status-${status}">${statusText}</span></td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;

        document.getElementById('mainContent').innerHTML = tabela;

    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        mostrarErro(`Erro ao carregar produtos: ${error.message}`);
    }
}

// Inicialização
window.addEventListener('DOMContentLoaded', () => {
    atualizarData();
    carregarProjetos();

    // Atualizar data a cada minuto
    setInterval(atualizarData, 60000);
});

// Tratamento de erros globais
window.addEventListener('error', (event) => {
    console.error('Erro não tratado:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Promise não tratada:', event.reason);
});