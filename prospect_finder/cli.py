"""CLI: recherche de prospects et envoi de campagnes d'emails B2B."""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from .contact import find_contact_email
from .outreach import SmtpConfig, send_campaign
from .places import SECTOR_TO_PLACE_TYPE, search_nearby


def cmd_search(args: argparse.Namespace) -> None:
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise SystemExit("GOOGLE_PLACES_API_KEY manquante (voir .env.example)")

    place_type = SECTOR_TO_PLACE_TYPE.get(args.sector, args.sector)
    prospects = search_nearby(api_key, args.lat, args.lng, args.radius, place_type)

    rows = []
    for p in prospects:
        email = find_contact_email(p.website) if args.find_email else None
        rows.append({
            "name": p.name,
            "address": p.address,
            "phone": p.phone or "",
            "website": p.website or "",
            "email": email or "",
            "rating": p.rating or "",
        })

    out_path = Path(args.output)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "address", "phone", "website", "email", "rating"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} prospects trouvés -> {out_path}")


def cmd_send(args: argparse.Namespace) -> None:
    smtp_config = SmtpConfig(
        host=os.environ["SMTP_HOST"],
        port=int(os.environ.get("SMTP_PORT", "587")),
        username=os.environ["SMTP_USERNAME"],
        password=os.environ["SMTP_PASSWORD"],
        from_addr=os.environ["SMTP_FROM"],
    )

    summary = send_campaign(
        leads_csv=Path(args.leads),
        template_path=Path(args.template),
        service_name=args.service_name,
        subject=args.subject,
        smtp_config=smtp_config,
        suppression_path=Path(args.suppression_list),
        unsubscribe_note=args.unsubscribe_note,
        delay_seconds=args.delay,
        dry_run=not args.confirm,
    )

    print(summary)
    if summary["dry_run"]:
        print("\nAucun email envoyé (mode dry-run). Relancez avec --confirm pour envoyer réellement.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prospection locale: recherche + email B2B conforme RGPD/LCEN")
    sub = parser.add_subparsers(required=True)

    p_search = sub.add_parser("search", help="Recherche des prospects près d'un point")
    p_search.add_argument("--sector", required=True, choices=sorted(SECTOR_TO_PLACE_TYPE.keys()))
    p_search.add_argument("--lat", type=float, required=True)
    p_search.add_argument("--lng", type=float, required=True)
    p_search.add_argument("--radius", type=int, default=5000, help="Rayon en mètres (max 50000)")
    p_search.add_argument("--output", default="leads.csv")
    p_search.add_argument("--find-email", action="store_true", help="Tente de trouver un email public sur le site de chaque prospect")
    p_search.set_defaults(func=cmd_search)

    p_send = sub.add_parser("send", help="Envoie une campagne d'emails à partir d'un CSV de leads")
    p_send.add_argument("--leads", required=True, help="CSV généré par la commande search")
    p_send.add_argument("--template", default="templates/email_template.txt")
    p_send.add_argument("--service-name", required=True)
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--suppression-list", default="suppression_list.txt")
    p_send.add_argument("--unsubscribe-note", default="Répondez STOP à cet email pour ne plus être contacté.")
    p_send.add_argument("--delay", type=float, default=5.0, help="Délai en secondes entre deux envois")
    p_send.add_argument("--confirm", action="store_true", help="Envoie réellement les emails (sinon dry-run)")
    p_send.set_defaults(func=cmd_send)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
