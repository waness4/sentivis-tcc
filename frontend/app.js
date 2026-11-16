/* SentiVis — apresentação experimental V01/V04; apenas dados de backend.ui_server. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const state = { mode: 'analisar', last: null, requestSeq: 0 };
  const API = { info: '/api/ui/info', analisar: '/api/ui/analisar', comparar: '/api/ui/comparar' };
  const LIMIT = 5000;
  const EXAMPLES = {
    dedicada: 'A aluna é dedicada.',
    facil: 'A prova foi fácil.',
    negacao: 'A aluna não é dedicada.',
  };
  const STATUS = {
    PONTUACAO_EXPLORATORIA_NAO_VALIDADA: ['Pontuação exploratória disponível', 'A soma representa apenas os termos identificados, sem validação contextual.', 'ok'],
    SEM_COBERTURA: ['Sem cobertura lexical', 'Nenhuma entrada foi reconhecida. Isso não significa neutralidade.', 'warn'],
    ABSTENCAO_LEXICAL: ['Abstenção por conflito lexical', 'Uma ou mais ocorrências exigem revisão antes de atribuir pontuação.', 'warn'],
    ABSTENCAO_ALVO: ['Abstenção por alvo indefinido', 'A relação N0/N1 não foi estabelecida a partir do contexto.', 'warn'],
    ABSTENCAO_CONTEXTO: ['Abstenção por contexto', 'Há negação ou modificador sem regra contextual validada.', 'warn'],
    ABSTENCAO_CATEGORIA_GRAMATICAL: ['Abstenção gramatical', 'A classe da palavra não corresponde à entrada lexical.', 'warn'],
    ABSTENCAO_ANEXACAO_AMBIGUA: ['Ligação sintática ambígua', 'O papel da expressão avaliativa não pôde ser determinado com segurança.', 'warn'],
    ABSTENCAO_PAPEL_SINTATICO: ['Papel sintático não reconhecido', 'Não foi identificado um único adjunto elegível para a hipótese.', 'warn'],
    ABSTENCAO_HIPOTESE_NAO_AUTORIZADA: ['Hipótese não ativada', 'A classificação contextual exige ativação explícita.', 'warn'],
  };
  // A camada de apresentação explica códigos; ela nunca altera decisões do backend.
  const MOTIVOS = {
    nenhuma_correspondencia_lexical: 'Nenhuma palavra da frase teve correspondência lexical.',
    categoria_gramatical_incompativel: 'Uma palavra tem classe gramatical diferente da entrada encontrada no léxico.',
    sintagma_com_ligado_a_nome: 'A expressão introduzida por “com” foi ligada a um substantivo; o seu papel na frase permanece incerto.',
    sem_adjunto_com_unico_ligado_a_verbo: 'Não foi identificado um único complemento com “com” ligado ao verbo.',
    multiplos_adjuntos_com_avaliativos: 'Há mais de um complemento avaliativo possível.',
    hipotese_modo_nao_ativada: 'A hipótese sintática não foi ativada explicitamente.',
    ambiguidade_categoria: 'O léxico apresenta mais de uma interpretação de classe gramatical.',
    ambiguidade_lema: 'O termo pode corresponder a mais de uma forma de referência no léxico.',
    negacao_sem_escopo: 'Existe uma negação cujo alcance não foi determinado.',
    modificador_sem_escopo: 'Existe um modificador cujo alcance não foi determinado.',
    ambiguidade_polaridade: 'O léxico apresenta polaridades conflitantes para esta ocorrência.',
  };
  const POS = {
    NOUN: 'Substantivo', VERB: 'Verbo', ADJ: 'Adjetivo', ADV: 'Advérbio',
    PROPN: 'Nome próprio', ADP: 'Preposição', DET: 'Determinante',
    PRON: 'Pronome', AUX: 'Auxiliar', NUM: 'Numeral',
  };
  const PAPEIS = {
    anexacao_nominal_ambigua: 'Ligação a substantivo — incerta',
    adjunto_com_ligado_ao_verbo: 'Possível complemento ligado ao verbo',
    indeterminado: 'Não determinado',
  };
  function explicarMotivo(codigo) {
    return MOTIVOS[codigo] || `Motivo técnico sem descrição: ${String(codigo)}`;
  }
  function nomePos(codigo) {
    return POS[codigo] || (codigo ? `Categoria ${String(codigo)}` : 'Não identificada');
  }
  function nomePapel(codigo) {
    return PAPEIS[codigo] || (codigo ? `Papel não descrito (${String(codigo)})` : 'Não determinado');
  }
  function razoesHumanas(motivos) {
    return Array.isArray(motivos) ? motivos.map(explicarMotivo) : [];
  }
  function explicacaoResultado(data) {
    const status = data.status;
    const checagens = Array.isArray(data.checagens_contextuais) ? data.checagens_contextuais : [];
    const ambiguos = checagens.filter(x => x.papel_hipotetico === 'anexacao_nominal_ambigua');
    if (status === 'ABSTENCAO_ANEXACAO_AMBIGUA' && ambiguos.length) {
      const termos = ambiguos.map(x => `“${x.expressao}”`).join(', ');
      return `O léxico reconheceu ${termos}, mas a análise sintática não determinou com segurança como essa expressão se relaciona com a ação. Nenhuma pontuação foi atribuída.`;
    }
    if (status === 'ABSTENCAO_CATEGORIA_GRAMATICAL') {
      return 'Uma correspondência lexical não corresponde à classe gramatical estimada para a palavra na frase. O sistema preferiu não pontuar.';
    }
    if (status === 'ABSTENCAO_ALVO') {
      return 'O SentiLex exige a indicação manual de N0 ou N1. Sem ela, o sistema não determina qual alvo lexical está sendo consultado.';
    }
    if (status === 'SEM_COBERTURA') {
      return 'Não foram identificadas correspondências lexicais suficientes para esta consulta. Isso não permite concluir que a frase é neutra.';
    }
    if (status === 'ABSTENCAO_LEXICAL') {
      return 'As correspondências encontradas no léxico têm conflitos ou ambiguidades que impedem uma pontuação confiável.';
    }
    if (status === 'ABSTENCAO_CONTEXTO') {
      return 'Há negação ou outro modificador cujo efeito sobre a avaliação ainda não foi determinado.';
    }
    if (status === 'ABSTENCAO_PAPEL_SINTATICO') {
      return 'A estrutura exigida pela hipótese contextual não foi identificada com segurança. A frase permanece sem pontuação.';
    }
    if (status === 'ABSTENCAO_HIPOTESE_NAO_AUTORIZADA') {
      return 'Esta hipótese contextual precisa ser ativada explicitamente antes de produzir uma pontuação exploratória.';
    }
    if (status === 'PONTUACAO_EXPLORATORIA_NAO_VALIDADA') {
      if (data.pontuacao_exploratoria === 0) {
        return 'A pontuação exploratória resultou em zero. Isso não prova que a frase é neutra nem que não contém sentimentos.';
      }
      return 'Uma pontuação exploratória foi obtida a partir das correspondências lexicais e das regras selecionadas. Ela não é uma classificação validada do sentido integral da frase.';
    }
    return 'A consulta não permite afirmar, por si só, o sentimento da frase ou a existência de viés.';
  }
  function interpretacao(data, compacto = false) {
    const filtro = data.filtragem_neutros_pos || {};
    const descartados = Array.isArray(filtro.descartados) ? filtro.descartados : [];
    const detalhe = descartados.length ? `<p class="interpretation-detail">O filtro ignorou a correspondência neutra ${descartados.map(x => `“${esc(x.expressao)}”`).join(', ')} por incompatibilidade gramatical. Isso não elimina outras incertezas.</p>` : '';
    return `<section class="interpretation-panel${compacto ? ' compact' : ''}" aria-label="Explicação do resultado">
      <h4>Como interpretar este resultado</h4>
      <p>${esc(explicacaoResultado(data))}</p>${detalhe}
    </section>`;
  }
  function coberturaNota(data, compacto = false) {
    const cobertos = data.tokens_cobertos;
    const totais = data.tokens_totais;
    const detalhamento = Number.isInteger(cobertos) && Number.isInteger(totais) && totais > 0
      ? `${cobertos} de ${totais} tokens tiveram correspondência lexical superficial. ` : '';
    return `<p class="coverage-note${compacto ? ' compact' : ''}">${esc(detalhamento)}Cobertura lexical não é acurácia, confiança nem percentual de sentimento. Uma correspondência descartada também pode constar na cobertura.</p>`;
  }
  function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  }
  function pct(value) {
    return typeof value === 'number' && Number.isFinite(value) ? `${(100 * value).toLocaleString('pt-BR', {maximumFractionDigits: 1})}%` : '—';
  }
  function num(value) { return typeof value === 'number' ? String(value) : '—'; }
  function getTarget() { return $('lexico').value === 'sentilex' ? $('alvo').value || null : null; }
  function getMethod() { return $('lexico').value === 'sentilex' ? $('metodo').value : 'aditivo_v01'; }
  function getOptions() {
    const metodo = getMethod(), alvo = getTarget();
    const hipotese_modo = metodo === 'contextual_v04' && $('hipotese-modo').checked;
    if (metodo === 'contextual_v04' && (!alvo || !hipotese_modo)) {
      $('results').innerHTML = '<div class="error-message" role="alert">Para usar a V04, selecione N0/N1 manualmente e marque a ativação explícita da hipótese sintática.</div>';
      return null;
    }
    return { lexico: $('lexico').value, alvo, metodo, hipotese_modo };
  }
  function textLength(id, label) {
    const el = $(id);
    const update = () => { $(label).textContent = `${el.value.length.toLocaleString('pt-BR')} / ${LIMIT.toLocaleString('pt-BR')}`; };
    el.addEventListener('input', update); update();
  }
  function updateLexicon() {
    const selected = $('lexico').value;
    $('alvo-field').hidden = selected !== 'sentilex';
    $('metodo-field').hidden = selected !== 'sentilex';
    if (selected !== 'sentilex') {
      $('metodo').value = 'aditivo_v01';
      $('alvo').value = '';
      $('hipotese-modo').checked = false;
    }
    $('lexico-hint').textContent = selected === 'sentilex'
      ? 'Registra polaridades por alvo N0/N1 e flexões de palavras.'
      : 'Recurso lexical com polaridade global por entrada.';
    updateMethod();
  }
  function updateMethod() {
    const v04 = getMethod() === 'contextual_v04';
    $('hipotese-field').hidden = !v04;
    if (!v04) $('hipotese-modo').checked = false;
    $('method-tag').textContent = v04
      ? 'SENTILEX · V04 · HIPÓTESE NÃO VALIDADA'
      : 'BASELINE ADITIVO · V0.1 · EXPLORATÓRIO';
    clearResults();
  }
  function switchTab(mode) {
    state.mode = mode;
    for (const v of ['analisar', 'comparar']) {
      const active = mode === v;
      $('tab-' + v).classList.toggle('active', active);
      $('tab-' + v).setAttribute('aria-selected', String(active));
      $('pane-' + v).hidden = !active;
    }
    clearResults();
  }
  function clearResults() {
    state.requestSeq += 1;
    state.last = null;
    $('results').innerHTML = '<div class="empty-state"><div class="empty-art" aria-hidden="true"><span class="orbit orbit-one"></span><span class="orbit orbit-two"></span><span class="orbit-core">S</span></div><h3>Pronto para explorar.</h3><p>Insira um texto ou selecione um exemplo para visualizar a cobertura lexical, os termos encontrados e as decisões do modelo.</p></div>';
  }
  async function fetchJson(url, init = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(url, { ...init, signal: controller.signal });
      const value = await response.json();
      if (!response.ok) {
        let detail = value.detail;
        if (Array.isArray(detail)) detail = detail.map(x => x.msg).join('; ');
        throw new Error(typeof detail === 'string' ? detail : `Erro HTTP ${response.status}`);
      }
      return value;
    } finally { clearTimeout(timeout); }
  }
  async function updateAvailability() {
    try {
      const info = await fetchJson(API.info);
      for (const name of ['oplexicon', 'sentilex']) {
        const el = $('avail-' + name), found = info.lexicos_arquivos_presentes?.[name];
        el.textContent = found ? 'Arquivo presente' : 'Pendente';
        el.className = 'availability ' + (found ? 'ready' : 'missing');
      }
    } catch {
      for (const name of ['oplexicon', 'sentilex']) {
        const el = $('avail-' + name); el.textContent = 'Indisponível'; el.className = 'availability missing';
      }
    }
  }
  function header(title, subtitle) {
    return `<div class="result-heading"><div><h3>${esc(title)}</h3><p>${esc(subtitle)}</p></div><button class="download-btn" id="download-result" type="button">Exportar JSON</button></div>`;
  }
  function banner(status, motivos = []) {
    const [title, message, type] = STATUS[status] || ['Resultado exploratório', 'Interpretação limitada pelo protocolo experimental.', 'warn'];
    const causes = Array.isArray(motivos) && motivos.length ? ` Motivos: ${razoesHumanas(motivos).map(esc).join(' ')}` : '';
    return `<div class="status-banner ${type === 'ok' ? '' : 'warn'}"><strong>${esc(title)}</strong><span>${esc(message)}${causes}</span></div>`;
  }
  function metric(label, value, progress = null) {
    const meter = typeof progress === 'number'
      ? `<div class="meter" role="meter" aria-label="${esc(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(progress * 100)}"><span style="width:${Math.max(0, Math.min(100, progress * 100))}%"></span></div>`
      : '';
    return `<div class="metric"><span>${esc(label)}</span><strong>${esc(value)}</strong>${meter}</div>`;
  }
  function termsTable(terms = [], compact = false) {
    if (!terms.length) return '<p class="field-hint">Nenhum termo recebeu pontuação.</p>';
    const rows = terms.map(x => {
      const pol = x.polaridade, label = pol === 1 ? '+1' : pol === -1 ? '−1' : '0';
      const tone = pol === 1 ? 'tone-pos' : pol === -1 ? 'tone-neg' : 'tone-neu';
      return `<tr><td>${esc(x.expressao)}</td>${compact ? '' : `<td>${esc(x.fonte)}</td>`}<td class="${tone}">${label}</td></tr>`;
    }).join('');
    return `<table class="term-table"><thead><tr><th>Termo</th>${compact ? '' : '<th>Origem</th>'}<th>Polaridade</th></tr></thead><tbody>${rows}</tbody></table>`;
  }
  function chips(words) {
    if (!Array.isArray(words) || !words.length) return '<p class="field-hint">Nenhum termo.</p>';
    return `<div class="chips">${words.map(word => `<span class="chip">${esc(word)}</span>`).join('')}</div>`;
  }
  function technical(data) {
    return `<details class="technical-details"><summary>Detalhes técnicos e proveniência dos dados</summary><pre>${esc(JSON.stringify({metodo:data.metodo, status:data.status, motivos:data.motivos, filtragem_neutros_pos:data.filtragem_neutros_pos, checagens_contextuais:data.checagens_contextuais, manifesto_fontes:data.manifesto_fontes, etiquetador:data.etiquetador, validacao_cientifica:data.validacao_cientifica}, null, 2))}</pre></details>`;
  }
  function contextual(data) {
    if (!data || !String(data.metodo || '').includes('v0.4')) return '';
    const checagens = Array.isArray(data.checagens_contextuais) ? data.checagens_contextuais : [];
    const filtro = data.filtragem_neutros_pos || {};
    const descartados = Array.isArray(filtro.descartados) ? filtro.descartados : [];
    const linhas = checagens.map(x => `<tr><td>${esc(x.expressao)}</td><td>${esc(nomePos(x.pos))}</td><td>${esc(nomePapel(x.papel_hipotetico))}</td><td>${esc(x.motivo ? explicarMotivo(x.motivo) : 'Sem impedimento gramatical nesta correspondência')}</td></tr>`).join('');
    return `<div class="result-block context-panel"><h4>Diagnóstico contextual V04</h4>
      <p class="field-hint">As categorias e ligações são estimativas do analisador linguístico, não confirmação do significado da frase ou do alvo N0/N1.</p>
      ${descartados.length ? `<p class="context-discarded">Entradas neutras ignoradas na decisão por incompatibilidade gramatical: ${descartados.map(x => esc(x.expressao)).join(', ')}.</p>` : ''}
      ${checagens.length ? `<div class="context-table-wrap"><table class="term-table context-table"><thead><tr><th>Termo</th><th>Classe gramatical estimada</th><th>Ligação estimada</th><th>Observação</th></tr></thead><tbody>${linhas}</tbody></table></div>` : '<p class="field-hint">Nenhuma checagem sintática disponível.</p>'}
    </div>`;
  }
  function renderSingle(data) {
    const score = num(data.pontuacao_exploratoria);
    const cls = data.classe_exploratoria || 'Abstenção';
    return header('Resultado da análise', 'Consulta lexical e soma exploratória, quando permitida.') +
      banner(data.status, data.motivos) + interpretacao(data) +
      `<div class="metrics">${metric('Pontuação (exploratória)', score)}${metric('Classe (exploratória)', cls)}${metric('Cobertura lexical superficial', pct(data.cobertura_superficial), data.cobertura_superficial)}</div>` + coberturaNota(data) +
      `<div class="result-block"><h4>Termos pontuados</h4>${termsTable(data.termos_pontuados)}</div>` +
      `<div class="result-block"><h4>Termos sem correspondência</h4>${chips(data.termos_sem_correspondencia)}</div>` +
      ((data.marcadores_de_negacao || []).length || (data.marcadores_de_modificacao || []).length ? `<div class="result-block"><h4>Marcadores contextuais detectados</h4>${chips([...(data.marcadores_de_negacao || []), ...(data.marcadores_de_modificacao || [])])}</div>` : '') +
      contextual(data) +
      `<div class="soft-note">Pontuações não validadas cientificamente. Uma ausência lexical não representa sentimento neutro. Este sistema não determina viés de gênero.</div>` + technical(data);
  }
  function compareCard(data, label) {
    const score = num(data.pontuacao_exploratoria);
    const abstained = data.pontuacao_exploratoria === null || data.pontuacao_exploratoria === undefined;
    const labelClass = abstained ? 'card-abstention' : 'card-scored';
    const status = abstained ? 'Abstenção — sem pontuação' : 'Pontuação exploratória';
    const coverage = typeof data.cobertura_superficial === 'number' ? data.cobertura_superficial : 0;
    const reasons = (Array.isArray(data.motivos) && data.motivos.length)
      ? `<p class="compare-reasons">${razoesHumanas(data.motivos).map(esc).join(' ')}</p>` : '';
    return `<article class="compare-card ${labelClass}">
      <div class="mini-kicker">${esc(label.toUpperCase())}</div>
      <h4>${esc(data.texto)}</h4>
      <div class="compare-score-label">${esc(status)}</div>
      <div class="compare-score">${esc(score)}</div>
      <div class="compare-caption">${esc(data.classe_exploratoria ? data.classe_exploratoria + ' (exploratória)' : 'Sem classificação automática')}</div>
      <div class="compare-coverage"><div class="compare-coverage-label"><span>Cobertura lexical superficial</span><strong>${esc(pct(data.cobertura_superficial))}</strong></div><div class="meter" role="meter" aria-label="Cobertura superficial — ${esc(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(coverage * 100)}"><span style="width:${Math.max(0,Math.min(100,coverage*100))}%"></span></div></div>
      ${reasons}${interpretacao(data, true)}${coberturaNota(data, true)}
      <div class="compare-terms"><h5>Termos pontuados</h5>${termsTable(data.termos_pontuados, true)}</div>
      ${contextual(data)}
      </article>`;
  }
  function renderCompare(data) {
    const calculable = data.ambas_pontuaveis === true && typeof data.delta_feminino_masculino_exploratorio === 'number';
    const delta = calculable ? num(data.delta_feminino_masculino_exploratorio) : 'Não calculável';
    const deltaExplainer = !calculable
      ? 'Ao menos uma análise se absteve; não existe diferença numérica calculável.'
      : data.delta_feminino_masculino_exploratorio === 0
        ? 'Este par não apresentou diferença na soma exploratória; isso não demonstra ausência de viés.'
        : 'Há diferença na soma exploratória deste par, sem inferência causal ou estatística de viés.';
    return header('Comparação de referências de gênero', 'Resultado descritivo e não validado cientificamente.') +
      `<div class="compare-guidance" role="note"><strong>Interpretação responsável</strong><span>A equivalência semântica dos textos digitados não foi verificada. A diferença exibida, quando calculável, é apenas descritiva e não mede viés de gênero.</span></div>` +
      `<div class="compare-results">${compareCard(data.feminina,'Referência feminina')}${compareCard(data.masculina,'Referência masculina')}</div>` +
      `<div class="delta-panel"><div><span class="delta-label">Diferença descritiva (feminino − masculino)</span><p>${esc(deltaExplainer)}</p></div><strong>${esc(delta)}</strong></div>` +
      `<div class="soft-note">${esc(data.aviso || 'Nenhum resultado isolado constitui evidência de viés.')}</div>` +
      `<details class="technical-details"><summary>Status individual, termos ausentes e proveniência</summary><div class="result-block"><h4>Feminina — ${esc(data.feminina.status)}</h4>${chips(data.feminina.termos_sem_correspondencia)}</div><div class="result-block"><h4>Masculina — ${esc(data.masculina.status)}</h4>${chips(data.masculina.termos_sem_correspondencia)}</div><pre>${esc(JSON.stringify({metodo:data.metodo, manifesto_fontes:data.manifesto_fontes, etiquetador:data.etiquetador, validacao_cientifica:data.validacao_cientifica}, null, 2))}</pre></details>`;
  }
  function downloadJson() {
    if (!state.last) return;
    const text = JSON.stringify(state.last, null, 2) + '\n';
    const blob = new Blob([text], { type: 'application/json;charset=utf-8' });
    const href = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = href; a.download = `sentivis_${state.mode}_exploratorio.json`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(href), 5000);
  }
  async function submit(mode, payload) {
    const seq = ++state.requestSeq;
    const button = $('btn-' + mode);
    button.disabled = true; button.setAttribute('aria-busy', 'true');
    $('results').innerHTML = '<div class="loading" role="status">Processando o texto com os léxicos locais…</div>';
    try {
      const result = await fetchJson(API[mode], { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (seq !== state.requestSeq || mode !== state.mode) return;
      state.last = result; state.mode = mode;
      $('results').innerHTML = mode === 'analisar' ? renderSingle(result) : renderCompare(result);
      $('download-result')?.addEventListener('click', downloadJson);
    } catch (error) {
      if (seq !== state.requestSeq || mode !== state.mode) return;
      state.last = null;
      const msg = error.name === 'AbortError' ? 'A requisição ultrapassou o tempo limite. Reinicie o servidor e tente novamente.' : error.message;
      $('results').innerHTML = `<div class="error-message" role="alert"><strong>Não foi possível concluir a consulta.</strong><div style="margin-top:6px">${esc(msg)}</div></div>`;
    } finally { button.disabled = false; button.removeAttribute('aria-busy'); }
  }
  function setup() {
    $('lexico').addEventListener('change', updateLexicon);
    $('metodo').addEventListener('change', updateMethod);
    $('hipotese-modo').addEventListener('change', clearResults);
    $('hero-compare').addEventListener('click', () => {
      switchTab('comparar');
      $('workspace-title').scrollIntoView({ behavior: 'smooth', block: 'start' });
      $('frase-feminina').focus({ preventScroll: true });
    });
    $('alvo').addEventListener('change', clearResults);
    ['analisar', 'comparar'].forEach(mode => $('tab-' + mode).addEventListener('click', () => switchTab(mode)));
    textLength('texto', 'length-texto'); textLength('frase-feminina', 'length-feminina'); textLength('frase-masculina', 'length-masculina');
    document.querySelectorAll('[data-example]').forEach(btn => btn.addEventListener('click', () => {
      $('texto').value = EXAMPLES[btn.dataset.example]; $('texto').dispatchEvent(new Event('input')); $('texto').focus();
    }));
    $('load-pair').addEventListener('click', () => {
      $('frase-feminina').value = 'A aluna é dedicada.';
      $('frase-masculina').value = 'O aluno é dedicado.';
      for (const id of ['frase-feminina', 'frase-masculina']) $(id).dispatchEvent(new Event('input'));
    });
    $('form-analisar').addEventListener('submit', (e) => {
      e.preventDefault(); const texto = $('texto').value.trim();
      if (!texto) { $('texto').focus(); return; }
      const options = getOptions();
      if (options) submit('analisar', { texto, ...options });
    });
    $('form-comparar').addEventListener('submit', (e) => {
      e.preventDefault(); const feminina = $('frase-feminina').value.trim(), masculina = $('frase-masculina').value.trim();
      if (!feminina) { $('frase-feminina').focus(); return; }
      if (!masculina) { $('frase-masculina').focus(); return; }
      const options = getOptions();
      if (options) submit('comparar', { feminina, masculina, ...options });
    });
    updateLexicon(); updateAvailability();
  }
  document.addEventListener('DOMContentLoaded', setup);
})();
