"""Recherche de prospects via l'API Google Places (Nearby Search)."""
from __future__ import annotations

import time
from dataclasses import dataclass, asdict

import requests

NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Types Google Places couramment utiles pour ce cas d'usage.
SECTOR_TO_PLACE_TYPE = {
    "restaurant": "restaurant",
    "artisan": "electrician",  # ajuster selon l'artisanat visé (plumber, painter, ...)
    "medical": "doctor",
}


@dataclass
class Prospect:
    place_id: str
    name: str
    address: str
    phone: str | None
    website: str | None
    rating: float | None


def search_nearby(api_key: str, lat: float, lng: float, radius_m: int, place_type: str) -> list[Prospect]:
    """Retourne les établissements d'un type donné dans un rayon autour d'un point.

    Fait jusqu'à 3 pages (limite imposée par l'API Places) et enrichit chaque
    résultat via Place Details pour récupérer téléphone/site web.
    """
    prospects: list[Prospect] = []
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "type": place_type,
        "key": api_key,
    }

    while True:
        resp = requests.get(NEARBY_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Erreur Google Places API: {data.get('status')} - {data.get('error_message', '')}")

        for result in data.get("results", []):
            prospects.append(_to_prospect(api_key, result))

        next_token = data.get("next_page_token")
        if not next_token:
            break

        # Google exige un court délai avant que le next_page_token soit valide.
        time.sleep(2)
        params = {"pagetoken": next_token, "key": api_key}

    return prospects


def _to_prospect(api_key: str, result: dict) -> Prospect:
    place_id = result["place_id"]
    details = _get_details(api_key, place_id)
    return Prospect(
        place_id=place_id,
        name=result.get("name", ""),
        address=result.get("vicinity", ""),
        phone=details.get("formatted_phone_number"),
        website=details.get("website"),
        rating=result.get("rating"),
    )


def _get_details(api_key: str, place_id: str) -> dict:
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website",
        "key": api_key,
    }
    resp = requests.get(DETAILS_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", {})


def prospects_to_dicts(prospects: list[Prospect]) -> list[dict]:
    return [asdict(p) for p in prospects]
