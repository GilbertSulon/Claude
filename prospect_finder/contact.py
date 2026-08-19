"""Recherche best-effort d'un email de contact sur le site public d'un prospect.

Ne consulte que la page d'accueil et une éventuelle page "contact" du site
indiqué par Google Places (donné volontairement par l'établissement comme
son site public). Respecte robots.txt et un timeout court ; n'insiste pas
en cas d'échec.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.robotparser

import requests

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
CANDIDATE_PATHS = ["", "/contact", "/contact-us", "/contactez-nous"]


def find_contact_email(website: str, timeout: int = 8) -> str | None:
    if not website:
        return None

    parsed = urllib.parse.urlparse(website)
    base = f"{parsed.scheme}://{parsed.netloc}"

    if not _robots_allow(base, timeout):
        return None

    for path in CANDIDATE_PATHS:
        url = base + path
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "ProspectFinderBot/1.0"})
        except requests.RequestException:
            continue
        if resp.status_code != 200:
            continue
        match = EMAIL_RE.search(resp.text)
        if match:
            return match.group(0)

    return None


def _robots_allow(base_url: str, timeout: int) -> bool:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url + "/robots.txt")
    try:
        rp.read()
    except Exception:
        # Pas de robots.txt lisible : on autorise par défaut.
        return True
    return rp.can_fetch("ProspectFinderBot/1.0", base_url)
