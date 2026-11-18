"""Filtres de gabarit : rendu Markdown sécurisé avec prise en charge du LaTeX."""
import re

import markdown as md
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# $$…$$, \[…\], \(…\) et $…$ (sur une ligne)
_MATH = re.compile(r"(\$\$.+?\$\$|\\\[.+?\\\]|\\\(.+?\\\)|(?<!\\)\$[^$\n]+?\$)", re.DOTALL)


@register.filter(name="markdown")
def markdown_filter(texte):
    """Convertit du Markdown en HTML.

    Le HTML saisi par l'utilisateur est échappé (pas d'injection de script)
    et les formules mathématiques sont protégées pour être rendues par KaTeX.
    """
    if not texte:
        return ""
    formules = []

    def _proteger(m):
        formules.append(m.group(0))
        return f"MATHXPLACEHOLDER{len(formules) - 1}X"

    texte = _MATH.sub(_proteger, texte)
    html = md.markdown(escape(texte), extensions=["extra", "sane_lists", "nl2br"], output_format="html")
    for i, formule in enumerate(formules):
        html = html.replace(f"MATHXPLACEHOLDER{i}X", escape(formule))
    return mark_safe(html)


@register.filter
def taille_lisible(octets):
    try:
        octets = float(octets)
    except (TypeError, ValueError):
        return ""
    for unite in ("o", "Ko", "Mo", "Go"):
        if octets < 1024:
            return f"{octets:.0f} {unite}" if unite == "o" else f"{octets:.1f} {unite}".replace(".", ",")
        octets /= 1024
    return f"{octets:.1f} To"
