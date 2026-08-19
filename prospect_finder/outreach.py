"""Envoi d'emails de prospection B2B, avec garde-fous légaux (RGPD/LCEN).

- Dry-run par défaut : rien n'est envoyé sans --confirm explicite côté CLI.
- Liste de suppression : les destinataires déjà contactés ou ayant demandé
  à être retirés ne sont plus jamais recontactés.
- Lien/mention de désinscription obligatoire dans le template.
- Délai entre chaque envoi pour rester raisonnable.
"""
from __future__ import annotations

import csv
import smtplib
import time
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path


@dataclass
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    from_addr: str
    use_tls: bool = True


def load_suppression_list(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def append_to_suppression_list(path: Path, email: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(email.strip().lower() + "\n")


def render_template(template: str, business_name: str, service_name: str, unsubscribe_note: str) -> str:
    return template.format(
        business_name=business_name,
        service_name=service_name,
        unsubscribe_note=unsubscribe_note,
    )


def send_campaign(
    leads_csv: Path,
    template_path: Path,
    service_name: str,
    subject: str,
    smtp_config: SmtpConfig,
    suppression_path: Path,
    unsubscribe_note: str,
    delay_seconds: float = 5.0,
    dry_run: bool = True,
) -> dict:
    """Parcourt un CSV de leads (colonnes: name, address, phone, website, email)
    et envoie un email personnalisé à chaque adresse valide et non supprimée.

    Retourne un résumé {sent, skipped_no_email, skipped_suppressed, dry_run}.
    """
    template = template_path.read_text(encoding="utf-8")
    suppressed = load_suppression_list(suppression_path)

    summary = {"sent": 0, "skipped_no_email": 0, "skipped_suppressed": 0, "dry_run": dry_run}

    server = None
    if not dry_run:
        server = smtplib.SMTP(smtp_config.host, smtp_config.port, timeout=15)
        if smtp_config.use_tls:
            server.starttls()
        server.login(smtp_config.username, smtp_config.password)

    try:
        with leads_csv.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row.get("email") or "").strip().lower()
                name = row.get("name", "")

                if not email:
                    summary["skipped_no_email"] += 1
                    continue
                if email in suppressed:
                    summary["skipped_suppressed"] += 1
                    continue

                body = render_template(template, name, service_name, unsubscribe_note)

                if dry_run:
                    print(f"[DRY-RUN] -> {email} ({name})\n{body}\n{'-' * 40}")
                else:
                    msg = EmailMessage()
                    msg["Subject"] = subject
                    msg["From"] = smtp_config.from_addr
                    msg["To"] = email
                    msg.set_content(body)
                    server.send_message(msg)
                    append_to_suppression_list(suppression_path, email)
                    time.sleep(delay_seconds)

                summary["sent"] += 1
    finally:
        if server is not None:
            server.quit()

    return summary
