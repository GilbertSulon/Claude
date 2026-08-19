# Claude
# Gilbert Test

## Prospect Finder — recherche et prospection locale (restos, artisans, médical)

Outil en deux étapes pour trouver des professionnels près d'un point donné
et leur envoyer une prospection par email conforme au droit français/UE.

### 1. Installation

```bash
pip install -r requirements.txt
cp .env.example .env   # puis remplir les clés
export $(cat .env | xargs)
```

Vous avez besoin d'une clé [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
(offre un quota gratuit mensuel) pour la recherche de prospects.

### 2. Rechercher des prospects

```bash
python -m prospect_finder.cli search \
  --sector restaurant \
  --lat 48.8566 --lng 2.3522 \
  --radius 5000 \
  --find-email \
  --output leads.csv
```

Secteurs disponibles : `restaurant`, `artisan`, `medical` (voir/ajuster le
mapping vers les types Google Places dans `prospect_finder/places.py`).

`--find-email` tente, de façon best-effort et en respectant `robots.txt`,
de trouver un email public sur le site déclaré de chaque établissement.
Beaucoup de fiches n'auront pas d'email trouvé — c'est normal, complétez
manuellement le CSV si besoin.

### 3. Envoyer une campagne

Adaptez d'abord `templates/email_template.txt`, puis testez en dry-run
(par défaut, **rien n'est envoyé**) :

```bash
python -m prospect_finder.cli send \
  --leads leads.csv \
  --service-name "mon service de ..." \
  --subject "Une question rapide" \
  --delay 5
```

Quand le rendu vous convient, ajoutez `--confirm` pour envoyer réellement :

```bash
python -m prospect_finder.cli send \
  --leads leads.csv \
  --service-name "mon service de ..." \
  --subject "Une question rapide" \
  --delay 5 \
  --confirm
```

Chaque email envoyé est ajouté à `suppression_list.txt` pour ne jamais
recontacter deux fois la même adresse. Vous pouvez aussi y ajouter
manuellement toute adresse ayant demandé à ne plus être contactée.

### Cadre légal (France/UE) — à respecter impérativement

- **B2B uniquement** : cet outil est conçu pour de la prospection entre
  professionnels (restaurateurs, artisans, professionnels de santé en tant
  qu'entités professionnelles), pas vers des particuliers.
- **RGPD / LCEN art. 22** : la prospection par email B2B est autorisée sans
  consentement préalable si l'offre est en rapport avec l'activité
  professionnelle du destinataire et qu'un moyen de refus simple est
  proposé — d'où la mention de désinscription obligatoire dans le
  template et la liste de suppression.
- **Ne pas scraper les plateformes qui l'interdisent dans leurs CGU**
  (Google Maps, Pages Jaunes, etc.). Cet outil utilise l'API officielle
  Google Places, et ne visite que le site public déclaré par chaque
  établissement pour y chercher un email de contact, dans le respect de
  `robots.txt`.
- Gardez un rythme d'envoi raisonnable (`--delay`) et traitez toute
  demande de retrait immédiatement.
