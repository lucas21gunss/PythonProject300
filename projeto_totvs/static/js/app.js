// static/js/app.js

// --- ESTADO GLOBAL ---
let projetoSelecionado = null;
let celulaSelecionada = null;
let carrinho = []; // { codigo, descricao, quantidade, celula, projeto }
let produtosData = [];
let projetosData = [];

// --- INICIALIZAÇÃO ---
window.addEventListener('DOMContentLoaded', () => {
    atualizarData();
    carregarProjetos();

    // Fechar modal ao clicar fora
    document.getElementById('cartModal').addEventListener('click', (e) => {
        if (e.target.id === 'cartModal') {
            toggleCart();
        }
    });
});

function atualizarData() {
    const el = document.getElementById('currentDate');
    if (el) el.textContent = new Date().toLocaleDateString('pt-BR');
}

// --- NAVEGAÇÃO E CARREGAMENTO ---

async function carregarProjetos() {
    const lista = document.getElementById('projetosList');
    lista.innerHTML = '<li class="loading">Carregando projetos...</li>';

    try {
        const res = await fetch('/api/projetos');
        const dados = await res.json();

        if (dados.error) throw new Error(dados.error);
        if (dados.length === 0) {
            lista.innerHTML = '<li class="selection-item disabled">Nenhum projeto encontrado</li>';
            return;
        }

        projetosData = dados;
        renderizarProjetos(dados);

    } catch (e) {
        lista.innerHTML = '<li class="selection-item disabled">Erro ao carregar projetos</li>';
        console.error('Erro ao carregar projetos:', e);
    }
}

function renderizarProjetos(dados) {
    const lista = document.getElementById('projetosList');
    lista.innerHTML = dados.map(p => `
        <li class="selection-item" onclick="selecionarProjeto('${p.AF8_PROJET}', '${p.AF8_REVISA}', event)">
            <div class="selection-item-main">${p.AF8_PROJET}</div>
            <div class="selection-item-sub">${p.AF8_XNOMCL || ''} (Rev: ${p.AF8_REVISA})</div>
        </li>
    `).join('');
}

function filtrarProjetos() {
    const termo = document.getElementById('filterProjeto').value.toLowerCase();
    const filtrados = projetosData.filter(p =>
        p.AF8_PROJET.toLowerCase().includes(termo) ||
        (p.AF8_XNOMCL && p.AF8_XNOMCL.toLowerCase().includes(termo))
    );
    renderizarProjetos(filtrados);
}

async function selecionarProjeto(id, rev, event) {
    projetoSelecionado = { id, rev };
    celulaSelecionada = null;

    document.querySelectorAll('#projetosList .selection-item').forEach(el => el.classList.remove('selected'));
    event.currentTarget.classList.add('selected');

    document.getElementById('mainTitle').textContent = `Projeto: ${id}`;
    document.getElementById('mainContent').innerHTML = '<div class="empty-state">Selecione uma célula para visualizar os produtos</div>';

    // Carregar Células
    const lista = document.getElementById('celulasList');
    lista.innerHTML = '<li class="loading">Carregando células...</li>';

    try {
        const res = await fetch(`/api/celulas/${id}/${rev}`);
        const dados = await res.json();

        if (dados.length === 0) {
            lista.innerHTML = '<li class="selection-item disabled">Sem células disponíveis</li>';
            return;
        }

        lista.innerHTML = dados.map(c => `
            <li class="selection-item" onclick="selecionarCelula('${c.AFC_XPROD}', event)">
                <div class="selection-item-main">${c.AFC_XPROD}</div>
                <div class="selection-item-sub">Necessidade: ${c.AFA_QUANT || 0} | Entregue: ${c.CP_XQUPR || 0}</div>
            </li>
        `).join('');

    } catch(e) {
        lista.innerHTML = '<li class="selection-item disabled">Erro ao carregar células</li>';
        console.error('Erro ao carregar células:', e);
    }
}

async function selecionarCelula(celula, event) {
    celulaSelecionada = celula;

    document.querySelectorAll('#celulasList .selection-item').forEach(el => el.classList.remove('selected'));
    event.currentTarget.classList.add('selected');

    document.getElementById('mainTitle').textContent = `Projeto: ${projetoSelecionado.id} | Célula: ${celula}`;
    document.getElementById('mainContent').innerHTML = '<div class="loading">Carregando produtos...</div>';

    try {
        const res = await fetch(`/api/produtos/${projetoSelecionado.id}/${projetoSelecionado.rev}/${celula}`);
        const json = await res.json();

        produtosData = json.data || [];
        renderPainelProdutos(json.estatisticas || {});

    } catch(e) {
        document.getElementById('mainContent').innerHTML = `<div class="error-message">Erro ao carregar produtos: ${e.message}</div>`;
        console.error('Erro ao carregar produtos:', e);
    }
}

// --- RENDERIZAÇÃO DA TABELA DE PRODUTOS ---

function renderPainelProdutos(stats) {
    const totalNec = stats.total_necessidade || 0;
    const totalEnt = stats.total_entregue || 0;
    const totalPen = totalNec - totalEnt;
    const percGeral = stats.percentual_geral || 0;

    document.getElementById('mainContent').innerHTML = `
        <div class="stats-box">
            <div class="stat-item necessidade">
                <div class="stat-label">Necessidade</div>
                <div class="stat-value">${totalNec}</div>
            </div>
            <div class="stat-item entregue">
                <div class="stat-label">Entregue</div>
                <div class="stat-value">${totalEnt}</div>
            </div>
            <div class="stat-item pendente">
                <div class="stat-label">Pendente</div>
                <div class="stat-value">${totalPen}</div>
            </div>
            <div class="stat-item percentual">
                <div class="stat-label">Conclusão</div>
                <div class="stat-value">${percGeral}%</div>
            </div>
        </div>

        <div class="product-filters">
            <input type="text" id="productFilterCode" class="product-filter-input" 
                   placeholder="🔍 Buscar por código..." oninput="aplicarFiltros()">
            <input type="text" id="productFilterDesc" class="product-filter-input" 
                   placeholder="🔍 Buscar por descrição..." oninput="aplicarFiltros()">
            <label style="display:flex; align-items:center; gap:8px; font-size:13px; cursor:pointer;">
                <input type="checkbox" id="productFilterPending" onchange="aplicarFiltros()"> 
                ⏳ Apenas Pendentes
            </label>
        </div>

        <div class="table-container">
            <table class="products-table">
                <thead>
                    <tr>
                        <th>Selecionar</th>
                        <th>Código</th>
                        <th>Descrição</th>
                        <th>Necessidade</th>
                        <th>Entregue</th>
                        <th>Pendente</th>
                        <th>Quantidade</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="produtosBody"></tbody>
            </table>
        </div>
    `;

    aplicarFiltros();
}

function aplicarFiltros() {
    const fCode = document.getElementById('productFilterCode').value.toLowerCase();
    const fDesc = document.getElementById('productFilterDesc').value.toLowerCase();
    const fPend = document.getElementById('productFilterPending').checked;

    const filtrados = produtosData.filter(p => {
        const cod = (p.AFA_PRODUT || "").toLowerCase();
        const des = (p.AFA_XDESCR || "").toLowerCase();
        const pen = (p.AFA_QUANT || 0) - (p.CP_XQUPR || 0);

        const matchTexto = cod.includes(fCode) && des.includes(fDesc);
        const matchPend = fPend ? pen > 0 : true;

        return matchTexto && matchPend;
    });

    document.getElementById('produtosBody').innerHTML = filtrados.map(p => {
        const nec = p.AFA_QUANT || 0;
        const ent = p.CP_XQUPR || 0;
        const pen = nec - ent;
        const perc = nec > 0 ? Math.round((ent/nec)*100) : 0;

        let statusClass = 'pending';
        let statusText = 'Pendente';

        if (ent >= nec && nec > 0) {
            statusClass = 'complete';
            statusText = 'Completo';
        } else if (ent > 0) {
            statusClass = 'partial';
            statusText = `${perc}%`;
        }

        const isInCart = carrinho.find(c => c.codigo === p.AFA_PRODUT);
        const valInput = isInCart ? isInCart.quantidade : (pen > 0 ? pen : 0);
        const disabled = pen <= 0 && !isInCart;

        return `
            <tr ${disabled ? 'style="opacity: 0.5;"' : ''}>
                <td data-label="Sel.">
                    <input type="checkbox" 
                           data-codigo="${p.AFA_PRODUT}" 
                           ${disabled ? 'disabled' : ''} 
                           ${isInCart ? 'checked' : ''} 
                           onchange="toggleProduto(this, ${JSON.stringify(p).replace(/"/g, '&quot;')}, ${pen})">
                </td>
                <td data-label="Código"><strong>${p.AFA_PRODUT}</strong></td>
                <td data-label="Descrição">${p.AFA_XDESCR || ''}</td>
                <td data-label="Nec.">${nec}</td>
                <td data-label="Ent.">${ent}</td>
                <td data-label="Pen.">${pen}</td>
                <td data-label="Qtd.">
                    <div class="qty-container">
                        <button class="qty-btn" onclick="changeQty('${p.AFA_PRODUT}', -1, ${pen})" ${disabled ? 'disabled' : ''}>-</button>
                        <input type="number" 
                               id="qty_${p.AFA_PRODUT}" 
                               class="qty-input" 
                               value="${valInput}" 
                               min="0"
                               max="${pen}"
                               ${disabled ? 'disabled' : ''}
                               onchange="updateManualQty('${p.AFA_PRODUT}', this.value, ${pen})">
                        <button class="qty-btn" onclick="changeQty('${p.AFA_PRODUT}', 1, ${pen})" ${disabled ? 'disabled' : ''}>+</button>
                    </div>
                </td>
                <td data-label="Status">
                    <span class="status-badge status-${statusClass}">${statusText}</span>
                </td>
            </tr>
        `;
    }).join('');
}

// --- LÓGICA DO CARRINHO ---

function changeQty(codigo, delta, max) {
    const input = document.getElementById(`qty_${codigo}`);
    let v = parseInt(input.value) + delta;

    if (v < 0) v = 0;
    if (v > max) v = max;

    input.value = v;

    const item = carrinho.find(c => c.codigo === codigo);
    if (item) {
        item.quantidade = v;
        updateCartBadge();
        renderCart();
    }
}

function updateManualQty(codigo, valor, max) {
    let v = parseInt(valor) || 0;

    if (v > max) v = max;
    if (v < 0) v = 0;

    const input = document.getElementById(`qty_${codigo}`);
    input.value = v;

    const item = carrinho.find(c => c.codigo === codigo);
    if (item) {
        item.quantidade = v;
        updateCartBadge();
        renderCart();
    }
}

function toggleProduto(cb, prod, max) {
    if (cb.checked) {
        const qtd = parseInt(document.getElementById(`qty_${prod.AFA_PRODUT}`).value);

        if (qtd > 0 && qtd <= max) {
            carrinho.push({
                codigo: prod.AFA_PRODUT,
                descricao: prod.AFA_XDESCR || prod.AFA_PRODUT,
                quantidade: qtd,
                celula: celulaSelecionada,
                projeto: projetoSelecionado.id
            });
        } else {
            cb.checked = false;
            alert(`Quantidade inválida! Deve ser entre 1 e ${max}`);
            return;
        }
    } else {
        carrinho = carrinho.filter(c => c.codigo !== prod.AFA_PRODUT);
    }

    updateCartBadge();
    renderCart();
}

function toggleCart() {
    document.getElementById('cartModal').classList.toggle('active');
    renderCart();
}

function updateCartBadge() {
    document.getElementById('cartBadge').textContent = carrinho.length;
}

function renderCart() {
    const container = document.getElementById('cartItems');

    if (carrinho.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#999; padding:40px;">Carrinho vazio</p>';
        return;
    }

    container.innerHTML = carrinho.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-code">${item.codigo}</div>
                <div class="cart-item-desc">${item.descricao}</div>
                <div class="cart-item-qty">Quantidade: ${item.quantidade}</div>
                <div style="font-size: 11px; color: #999; margin-top: 4px;">
                    Célula: ${item.celula}
                </div>
            </div>
            <button class="remove-item" onclick="removeFromCart('${item.codigo}')">×</button>
        </div>
    `).join('');
}

function removeFromCart(codigo) {
    carrinho = carrinho.filter(c => c.codigo !== codigo);
    updateCartBadge();
    renderCart();

    const cb = document.querySelector(`input[data-codigo="${codigo}"]`);
    if (cb) cb.checked = false;

    aplicarFiltros();
}

function clearCart() {
    if (carrinho.length === 0) {
        alert('O carrinho já está vazio!');
        return;
    }

    if (confirm('Deseja realmente limpar todo o carrinho?')) {
        carrinho.forEach(item => {
            const cb = document.querySelector(`input[data-codigo="${item.codigo}"]`);
            if (cb) cb.checked = false;
        });

        carrinho = [];
        updateCartBadge();
        renderCart();
        aplicarFiltros();
    }
}

// --- ENVIO DA REQUISIÇÃO COM MODAL DE RETORNO ---

async function sendRequest() {
    if (carrinho.length === 0) {
        alert('❌ Selecione pelo menos um item antes de enviar!');
        return;
    }

    // Agrupa por projeto e célula
    const grupos = {};

    carrinho.forEach(item => {
        if (!grupos[item.projeto]) {
            grupos[item.projeto] = {};
        }
        if (!grupos[item.projeto][item.celula]) {
            grupos[item.projeto][item.celula] = [];
        }
        grupos[item.projeto][item.celula].push({
            produto: item.codigo,
            quantidade: item.quantidade
        });
    });

    // Confirmação
    const totalItens = carrinho.reduce((sum, item) => sum + item.quantidade, 0);
    const totalCelulas = Object.values(grupos).reduce((sum, proj) => sum + Object.keys(proj).length, 0);

    const confirmMsg = `Confirma o envio?\n\n` +
                      `📦 ${carrinho.length} produto(s)\n` +
                      `🔢 ${totalItens} unidade(s)\n` +
                      `🏭 ${totalCelulas} célula(s)`;

    if (!confirm(confirmMsg)) {
        return;
    }

    const btnSend = document.querySelector('.cart-footer .btn-send');
    const btnClear = document.querySelector('.cart-footer .btn-clear');

    if (btnSend) {
        btnSend.disabled = true;
        btnSend.textContent = '⏳ Enviando...';
    }
    if (btnClear) btnClear.disabled = true;

    try {
        // Monta payload dinâmico para cada projeto
        const requests = Object.keys(grupos).map(projeto => {
            const payload = {
                projeto: projeto,
                celulas: Object.keys(grupos[projeto]).map(celula => ({
                    celula: celula,
                    itens: grupos[projeto][celula]
                }))
            };

            console.log('📤 Enviando payload:', payload);

            return fetch('/api/requisicao', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        });

        // Aguarda todas as requisições
        const responses = await Promise.all(requests);
        const results = await Promise.all(responses.map(r => r.json()));

        console.log('📥 Respostas recebidas:', results);

        // Processa resultados
        const sucessos = results.filter(r => r.success);
        const erros = results.filter(r => !r.success);

        if (sucessos.length > 0) {
            // EXIBE MODAL COM RETORNO DO PROTHEUS
            mostrarModalRetorno(sucessos);

            // Limpa carrinho
            carrinho.forEach(item => {
                const cb = document.querySelector(`input[data-codigo="${item.codigo}"]`);
                if (cb) cb.checked = false;
            });

            carrinho = [];
            updateCartBadge();
            toggleCart();
            aplicarFiltros();
        }

        if (erros.length > 0) {
            const msgErro = erros.map(e => e.error).join('\n\n');
            alert(`❌ Erros encontrados:\n\n${msgErro}`);
        }

    } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        alert('❌ Erro de conexão com o servidor:\n\n' + error.message);

    } finally {
        if (btnSend) {
            btnSend.disabled = false;
            btnSend.textContent = 'Gerar OS';
        }
        if (btnClear) btnClear.disabled = false;
    }
}

// --- MODAL DE RETORNO DO PROTHEUS ---

function mostrarModalRetorno(resultados) {
    // Cria o modal dinamicamente
    const modal = document.createElement('div');
    modal.className = 'result-modal';
    modal.innerHTML = `
        <div class="result-content">
            <div class="result-header">
                <h2>✅ Ordem(ns) Gerada(s) com Sucesso!</h2>
                <button class="close-result" onclick="fecharModalRetorno()">×</button>
            </div>
            <div class="result-body">
                ${resultados.map((res, idx) => `
                    <div class="result-section">
                        <h3>📋 Retorno ${idx + 1}</h3>
                        <div class="result-message">${res.mensagem || 'Processado com sucesso'}</div>
                        ${res.dados_protheus ? `
                            <div class="result-data">
                                <h4>📊 Dados do Protheus:</h4>
                                <pre>${JSON.stringify(res.dados_protheus, null, 2)}</pre>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
            <div class="result-footer">
                <button class="btn-close-result" onclick="fecharModalRetorno()">Fechar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Anima entrada
    setTimeout(() => modal.classList.add('active'), 10);
}

function fecharModalRetorno() {
    const modal = document.querySelector('.result-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}