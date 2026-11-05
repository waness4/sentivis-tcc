"""Consulta lexical conservadora; NÃO classifica frases ou quantifica viés.

Mantém múltiplas interpretações, alvos N0/N1 e proveniência dos registros.
A consulta não decide o referente de opinião ou o sentido no contexto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

from backend.lexicon_audit import EntradaLexical
from backend.lexicon_triage import ler_para_curadoria, localizar_unico

ROOT = Path(__file__).resolve().parent.parent
ARQUIVOS = {
    "oplexicon": ("oplexicon", "lexico_v3.0.txt"),
    "sentilex_lem": ("sentilex_lem", "SentiLex-lem-PT02.txt"),
    "sentilex_flex": ("sentilex_flex", "SentiLex-flex-PT02.txt"),
}


def chave_termo(termo: str, categoria: str) -> str:
    """Evita fundir emoticons :p e :P, distintos no OpLexicon."""
    termo_nfc = unicodedata.normalize("NFC", termo.strip())
    if categoria.casefold().strip() == "emot":
        return termo_nfc
    return termo_nfc.casefold()


def _tem_papel_declarado(entrada: EntradaLexical, papel: str) -> bool:
    alvo = (entrada.alvo or "").upper()
    # Só reconhecemos, para consulta experimental, os papéis documentados N0/N1.
    return f":{papel}" in alvo and alvo.startswith("HUM:")


def _selecionadas(entradas: list[EntradaLexical], termo: str, *,
                  lexico: str) -> tuple[list[EntradaLexical], str]:
    selecionadas = [e for e in entradas if (
        e.origem in (('oplexicon',) if lexico == 'oplexicon' else ('sentilex_lem', 'sentilex_flex'))
        and chave_termo(e.termo, e.categoria) == chave_termo(termo, e.categoria)
    )]
    if lexico == 'sentilex':
        # Uma mesma entrada pode estar nas duas representações. Consultar
        # primeiramente o arquivo de formas, sem contar ambas em duplicidade.
        flex = [e for e in selecionadas if e.origem == 'sentilex_flex']
        if flex:
            return flex, 'sentilex_flex'
        return [e for e in selecionadas if e.origem == 'sentilex_lem'], 'sentilex_lem'
    return selecionadas, 'oplexicon'


def consultar_entradas(entradas: list[EntradaLexical], termo: str, *,
                       lexico: str, alvo: str | None = None) -> dict:
    """Inspeção de termo exato, sem desambiguação contextual ou classificação.

    `alvo` é obrigatório para afirmar consistência numérica no SentiLex.
    O retorno pode listar interpretações, mas NUNCA é uma pontuação de frase.
    """
    if lexico not in ('oplexicon', 'sentilex'):
        raise ValueError("Léxico deve ser 'oplexicon' ou 'sentilex'.")
    if not termo.strip():
        raise ValueError('Termo não pode ser vazio.')
    if lexico == 'sentilex' and alvo not in (None, 'N0', 'N1'):
        raise ValueError('Somente N0 e N1 são alvos de consulta suportados.')
    if lexico == 'oplexicon' and alvo not in (None, 'GLOBAL'):
        raise ValueError('OpLexicon não fornece alvos N0/N1.')
    papel = 'GLOBAL' if lexico == 'oplexicon' else alvo
    relevantes, fonte = _selecionadas(entradas, termo, lexico=lexico)
    avisos: list[str] = []
    if not relevantes:
        return {'termo': termo, 'lexico': lexico, 'alvo': papel,
                'fonte': fonte, 'status': 'sem_correspondencia',
                'polaridade_consulta': None, 'avisos': [], 'candidatos': []}

    candidatos = []
    for e in relevantes:
        candidatos.append({
            'arquivo': e.arquivo, 'linha': e.linha, 'termo': e.termo,
            'lema': e.lema, 'categoria': e.categoria, 'alvo_declarado': e.alvo,
            'polaridades': {p: v for p, v in e.polaridades},
            'flexao': e.flexao, 'anotacao': e.anotacao, 'revisao': e.revisao,
            'atributos_sem_chave': list(e.atributos_sem_chave),
        })
    if lexico == 'sentilex' and alvo is None:
        return {'termo': termo, 'lexico': lexico, 'alvo': None,
                'fonte': fonte, 'status': 'alvo_nao_informado',
                'polaridade_consulta': None,
                'avisos': ['O alvo N0/N1 depende da análise sintática/contextual.'],
                'candidatos': candidatos}

    consideradas = [e for e in relevantes if papel in dict(e.polaridades)]
    if not consideradas:
        return {'termo': termo, 'lexico': lexico, 'alvo': papel,
                'fonte': fonte, 'status': 'alvo_sem_entrada',
                'polaridade_consulta': None, 'avisos': ['Nenhum registro informa polaridade para o alvo.'],
                'candidatos': candidatos}

    polaridades = {dict(e.polaridades)[papel] for e in consideradas}
    categorias = {e.categoria.casefold() for e in consideradas}
    lemas = {unicodedata.normalize('NFC', e.lema or '').casefold() for e in consideradas}
    flags = []
    if not polaridades.issubset({-1, 0, 1}):
        flags.append('polaridade_fora_do_padrao')
    if lexico == 'sentilex' and any(not _tem_papel_declarado(e, papel) for e in consideradas):
        flags.append('alvo_inconsistente')
    if len(polaridades) > 1:
        flags.append('conflito_polaridade_mesmo_alvo')
    if len(categorias) > 1:
        flags.append('ambiguidade_categoria')
    if lexico == 'sentilex' and len(lemas) > 1:
        flags.append('ambiguidade_lema')
    if any(e.atributos_sem_chave for e in consideradas):
        flags.append('metadado_morfologico_pendente')
    if flags:
        avisos.append('Consulta lexical sem decisão automática: ' + ', '.join(flags))
    return {
        'termo': termo, 'lexico': lexico, 'alvo': papel, 'fonte': fonte,
        'status': 'revisao_necessaria' if flags else 'candidata_lexical_consistente',
        'motivos': flags,
        'polaridade_consulta': next(iter(polaridades)) if not flags else None,
        'avisos': avisos,
        'candidatos': candidatos,
    }


def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open('rb') as stream:
        for bloco in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(bloco)
    return h.hexdigest()


def carregar_para_consulta(raiz: Path, lexico: str) -> tuple[list[EntradaLexical], dict]:
    """Carrega SOMENTE fontes locais cujos SHA-256 correspondem à curadoria."""
    base = raiz / 'data' / 'lexicos'
    relatorio = base / 'relatorio_curadoria.json'
    if not relatorio.is_file():
        raise FileNotFoundError('Execute primeiro python -m backend.lexicon_triage.')
    dados = json.loads(relatorio.read_text(encoding='utf-8'))
    if dados.get('total_falhas_de_leitura') != 0:
        raise ValueError('Curadoria informa falhas de leitura; consulta bloqueada.')
    tipos = ('oplexicon',) if lexico == 'oplexicon' else ('sentilex_lem', 'sentilex_flex')
    entradas: list[EntradaLexical] = []
    manifest = {}
    for tipo in tipos:
        nome = ARQUIVOS[tipo][1]
        caminho = localizar_unico(base / 'originais', nome)
        sha = _sha256(caminho)
        esperado = dados.get('fontes', {}).get(tipo, {}).get('sha256')
        if not esperado or esperado.lower() != sha.lower():
            raise ValueError(f'SHA-256 não coincide com relatório de curadoria: {nome}')
        lidas, falhas = ler_para_curadoria(caminho, tipo)
        if falhas:
            raise ValueError(f'{nome} tem {len(falhas)} registros não interpretáveis.')
        entradas.extend(lidas)
        manifest[tipo] = {'arquivo': nome, 'sha256': sha, 'registros': len(lidas)}
    return entradas, manifest


def main():
    parser = argparse.ArgumentParser(description='Consulta lexical auditável, sem classificar frases')
    parser.add_argument('--termo', required=True)
    parser.add_argument('--lexico', required=True, choices=('oplexicon', 'sentilex'))
    parser.add_argument('--alvo', choices=('N0', 'N1'))
    parser.add_argument('--raiz', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), args.lexico)
        saida = consultar_entradas(entradas, args.termo, lexico=args.lexico, alvo=args.alvo)
        saida['fontes_verificadas'] = fontes
    except (ValueError, FileNotFoundError, UnicodeError) as exc:
        parser.exit(1, f'ERRO: {exc}\n')
    print(json.dumps(saida, indent=2, ensure_ascii=False))
    print('AVISO: inspeção lexical; resultado NÃO é classificação científica de frases.')


if __name__ == '__main__':
    main()
