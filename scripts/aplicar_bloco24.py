"""Aplica o Bloco 24 de apresentação sem alterar a análise científica.

Executar da raiz: python .\\scripts\\aplicar_bloco24.py
Só modifica frontend/index.html e frontend/styles.css.
"""
from __future__ import annotations

import argparse
from pathlib import Path

TEXTO_ANTIGO = "Versão de demonstração · v0.1"
TEXTO_NOVO = "Interface experimental · baselines V01 e V04"
MARCADOR_CSS = ".compare-card .term-table:not(.context-table) th:first-child,"
ESTILOS = """
/* O conteúdo técnico precisa continuar legível quando há dois cartões lado a lado. */
.context-table-wrap {{
  overflow-x: auto;
  max-width: 100%;
  scrollbar-width: thin;
}}
.context-table {{
  min-width: 660px;
  table-layout: auto;
}}
/* Evita a divisão de “Termo” e “gentileza” em linhas diferentes. */
.context-table th:first-child,
.context-table td:first-child {{
  min-width: 88px;
  white-space: nowrap;
  word-break: normal;
  overflow-wrap: normal;
}}
/* As colunas descritivas ainda podem quebrar frases entre palavras. */
.context-table th:not(:first-child),
.context-table td:not(:first-child) {{
  word-break: normal;
  overflow-wrap: break-word;
}}
/* A tabela compacta de termos pontuados também preserva termos inteiros. */
.compare-card .term-table:not(.context-table) th:first-child,
.compare-card .term-table:not(.context-table) td:first-child {{
  white-space: nowrap;
  overflow-wrap: normal;
  word-break: normal;
}}
""".lstrip("\n")


def preparar_alteracoes(raiz: Path) -> tuple[Path, str, Path, str]:
    raiz = Path(raiz)
    pagina = raiz / "frontend" / "index.html"
    estilo = raiz / "frontend" / "styles.css"
    conteudo = pagina.read_text(encoding="utf-8")
    css = estilo.read_text(encoding="utf-8")

    # Evita modificar versões imprevistas da interface.
    if TEXTO_ANTIGO in conteudo:
        if conteudo.count(TEXTO_ANTIGO) != 1:
            raise ValueError("Texto da versão aparece mais de uma vez no HTML")
        atualizado = conteudo.replace(TEXTO_ANTIGO, TEXTO_NOVO, 1)
    elif TEXTO_NOVO in conteudo:
        atualizado = conteudo
    else:
        raise ValueError("Não encontrei a indicação de versão esperada no frontend/index.html")

    if ".context-table-wrap" not in css or ".compare-card" not in css:
        raise ValueError("O CSS não corresponde à interface do Bloco 23")
    if css.count(MARCADOR_CSS) > 1:
        raise ValueError("Ajuste do Bloco 24 duplicado no CSS")
    css_atualizado = css if MARCADOR_CSS in css else css.rstrip("\n") + "\n\n" + ESTILOS
    return pagina, atualizado, estilo, css_atualizado


def aplicar(raiz: Path) -> list[str]:
    pagina, html, estilo, css = preparar_alteracoes(raiz)
    modificados = []
    if pagina.read_text(encoding="utf-8") != html:
        pagina.write_text(html, encoding="utf-8", newline="\n")
        modificados.append(str(pagina))
    if estilo.read_text(encoding="utf-8") != css:
        estilo.write_text(css, encoding="utf-8", newline="\n")
        modificados.append(str(estilo))
    return modificados


def main() -> None:
    parser = argparse.ArgumentParser(description="SentiVis Bloco 24 — ajuste visual não científico")
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        mod = aplicar(args.raiz.resolve())
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(1, f"ERRO: {exc}\nNenhum ajuste adicional deve ser aplicado sem revisar a versão local.\n")
    print("Bloco 24: ajustados" if mod else "Bloco 24: já aplicado; nenhum arquivo modificado")
    for p in mod:
        print("-", p)
    print("Sem alterações de classificadores, APIs ou dados de avaliação.")


if __name__ == "__main__":
    main()
