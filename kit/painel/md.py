# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Markdown para HTML, pequeno e seguro: escapa todo HTML do texto antes de formatar.

Cobre o que os arquivos do kit usam: títulos, parágrafos, listas, tabelas, citação, bloco de código, linha,
negrito, itálico, código e links (só http/https; caminho local vira código).
"""
import html
import re

_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_NEGRITO = re.compile(r"\*\*(.+?)\*\*")
_ITALICO = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")
_CODIGO = re.compile(r"`([^`]+)`")
_TABELA_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
_ITEM_UL = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_ITEM_OL = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_TITULO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def _inline(texto):
    """Formata uma linha já escapada. O código é separado antes para não receber negrito nem link."""
    partes = []

    def guarda(m):
        partes.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(partes) - 1}\x00"

    t = _CODIGO.sub(guarda, html.escape(texto, quote=True))

    def link(m):
        rotulo, url = m.group(1), html.unescape(m.group(2))
        if re.match(r"^https?://", url, re.I):
            return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{rotulo}</a>'
        return f"{rotulo} (<code>{html.escape(url)}</code>)"

    t = _LINK.sub(link, t)
    t = _NEGRITO.sub(r"<strong>\1</strong>", t)
    t = _ITALICO.sub(r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: partes[int(m.group(1))], t)


def _celulas(linha):
    s = linha.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


_COMENTARIO = re.compile(r"<!--.*?-->[ \t]*\n?", re.S)


_AUTORIA = re.compile(r"<!-- © [^\n]*?TVK-\d{4}-AF-[0-9A-F]{8} -->[ \t]*\n?")


def sem_comentarios(texto):
    """Tira os comentários HTML (o aviso de autoria do topo de cada guia): no painel eles apareceriam como texto."""
    return _COMENTARIO.sub("", str(texto or ""))


def sem_autoria(texto):
    """Tira só a linha de autoria do kit (nunca um comentário que o usuário escreveu)."""
    return _AUTORIA.sub("", str(texto or ""), count=1)


def para_html(md):
    """HTML seguro de um texto em markdown."""
    linhas = sem_comentarios(md).replace("\r\n", "\n").split("\n")
    saida, i, n = [], 0, len(linhas)
    while i < n:
        linha = linhas[i]
        s = linha.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            bloco = []
            i += 1
            while i < n and not linhas[i].strip().startswith("```"):
                bloco.append(linhas[i])
                i += 1
            i += 1
            saida.append(f"<pre><code>{html.escape(chr(10).join(bloco))}</code></pre>")
            continue
        m = _TITULO.match(s)
        if m:
            nivel = min(6, len(m.group(1)) + 1)
            saida.append(f"<h{nivel}>{_inline(m.group(2))}</h{nivel}>")
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            saida.append("<hr>")
            i += 1
            continue
        if s.startswith("|") and i + 1 < n and _TABELA_SEP.match(linhas[i + 1]):
            cab = _celulas(s)
            i += 2
            corpo = []
            while i < n and linhas[i].strip().startswith("|"):
                corpo.append(_celulas(linhas[i]))
                i += 1
            th = "".join(f"<th scope=\"col\">{_inline(c)}</th>" for c in cab)
            trs = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in corpo)
            saida.append(f'<div class="tabela"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if s.startswith(">"):
            bloco = []
            while i < n and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip()[1:].strip())
                i += 1
            saida.append(f"<blockquote>{para_html(chr(10).join(bloco))}</blockquote>")
            continue
        if _ITEM_UL.match(linha) or _ITEM_OL.match(linha):
            ordenada = bool(_ITEM_OL.match(linha)) and not _ITEM_UL.match(linha)
            itens = []
            while i < n and (_ITEM_UL.match(linhas[i]) or _ITEM_OL.match(linhas[i])
                             or (linhas[i].startswith("  ") and linhas[i].strip() and itens)):
                m = _ITEM_UL.match(linhas[i]) or _ITEM_OL.match(linhas[i])
                if m and len(m.group(1)) < 2:
                    itens.append(m.group(2))
                elif itens:
                    # Subitem vira "· texto" no item anterior; linha quebrada do mesmo item só continua a frase
                    itens[-1] += (" · " + m.group(2)) if m else (" " + linhas[i].strip())
                i += 1
            tag = "ol" if ordenada else "ul"
            itens_html = []
            for it in itens:
                marcado = re.match(r"^\[( |x|X)\]\s+(.*)$", it)
                if marcado:
                    feito = marcado.group(1).lower() == "x"
                    itens_html.append(f'<li class="tarefa{" feita" if feito else ""}">'
                                      f'<span aria-hidden="true">{"☑" if feito else "☐"}</span> {_inline(marcado.group(2))}</li>')
                else:
                    itens_html.append(f"<li>{_inline(it)}</li>")
            saida.append(f"<{tag}>{''.join(itens_html)}</{tag}>")
            continue
        par = [s]
        i += 1
        while i < n and linhas[i].strip() and not (
                linhas[i].strip().startswith(("#", "|", ">", "```")) or _ITEM_UL.match(linhas[i])
                or _ITEM_OL.match(linhas[i])):
            par.append(linhas[i].strip())
            i += 1
        saida.append(f"<p>{_inline(' '.join(par))}</p>")
    return "\n".join(saida)


def secao(md, titulo):
    """Trecho de um markdown entre o título `## titulo` e o próximo título do mesmo nível ou acima."""
    linhas = str(md or "").split("\n")
    alvo = titulo.strip().lower()
    dentro, nivel, saida = False, 0, []
    for linha in linhas:
        m = _TITULO.match(linha.strip())
        if m:
            if dentro and len(m.group(1)) <= nivel:
                break
            if not dentro and m.group(2).strip().lower().startswith(alvo):
                dentro, nivel = True, len(m.group(1))
                continue
        if dentro:
            saida.append(linha)
    return "\n".join(saida).strip()
