# -*- coding: utf-8 -*-
"""
Offline City & Country Validation using geonamescache.
Provides accent-insensitive and case-insensitive matching,
population-based disambiguation, ISO flag emoji generation,
and script-aware fallback prompts.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import geonamescache


def country_code_to_flag(code: Optional[str]) -> str:
    """Converts a 2-letter uppercase ISO country code to its flag emoji."""
    if not code or len(code) != 2 or not code.isalpha():
        return ""
    code = code.upper()
    return "".join(chr(0x1F1E6 + (ord(char) - ord("A"))) for char in code)


def strip_accents(text: str) -> str:
    """Removes diacritics/accents from text while preserving case."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_bytes = normalized.encode("ASCII", "ignore")
    return ascii_bytes.decode("utf-8").strip()


def has_cyrillic_or_persian(text: str) -> bool:
    """Checks if text contains Cyrillic or Arabic/Persian characters."""
    for ch in text:
        code = ord(ch)
        if 0x0400 <= code <= 0x04FF:  # Cyrillic
            return True
        if 0x0600 <= code <= 0x06FF or 0xFB50 <= code <= 0xFDFF or 0xFE70 <= code <= 0xFEFF:  # Arabic / Persian
            return True
    return False


@dataclass
class LocationMatch:
    city: str
    country_name: str
    country_code: str
    location_display: str
    population: int = 0
    geonameid: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "city": self.city,
            "country_name": self.country_name,
            "country_code": self.country_code,
            "location_display": self.location_display,
            "population": self.population,
            "geonameid": self.geonameid,
        }


class LocationResolver:
    """Offline lookup resolver built on top of geonamescache."""

    def __init__(self):
        self.gc = geonamescache.GeonamesCache()
        self.countries = self.gc.get_countries()
        self.cities = self.gc.get_cities()

        # Build country index: normalized country name -> country_dict
        self._country_index: Dict[str, Dict[str, Any]] = {}
        for iso, data in self.countries.items():
            name = data.get("name", "")
            self._country_index[strip_accents(name)] = data
            self._country_index[iso.lower()] = data

        # Common country aliases / overrides
        aliases = {
            "usa": "US",
            "united states": "US",
            "united states of america": "US",
            "uk": "GB",
            "united kingdom": "GB",
            "great britain": "GB",
            "russia": "RU",
            "russian federation": "RU",
            "iran": "IR",
            "islamic republic of iran": "IR",
            "indonesia": "ID",
            "india": "IN",
            "uae": "AE",
            "united arab emirates": "AE",
            "korea": "KR",
            "south korea": "KR",
        }
        for alias, iso in aliases.items():
            if iso in self.countries:
                self._country_index[alias] = self.countries[iso]

        # Primary city name index: exact normalized primary name -> list of city objects
        self._primary_city_index: Dict[str, List[Dict[str, Any]]] = {}
        # Alternate city name index: normalized name -> list of city objects
        self._alt_city_index: Dict[str, List[Dict[str, Any]]] = {}

        for gid, city_data in self.cities.items():
            primary_name = city_data.get("name", "")
            p_norm = strip_accents(primary_name).lower().strip()
            p_raw = primary_name.lower().strip()
            if p_norm:
                self._primary_city_index.setdefault(p_norm, []).append(city_data)
            if p_raw and p_raw != p_norm:
                self._primary_city_index.setdefault(p_raw, []).append(city_data)

            # Alternate names
            for alt in city_data.get("alternatenames", []):
                alt_raw = alt.lower().strip()
                if alt_raw:
                    self._alt_city_index.setdefault(alt_raw, []).append(city_data)
                alt_norm = strip_accents(alt).lower().strip()
                if alt_norm and alt_norm != alt_raw:
                    self._alt_city_index.setdefault(alt_norm, []).append(city_data)

    def resolve(self, query: str) -> Dict[str, Any]:
        """
        Resolves query to LocationMatch(es).
        Returns dict with status:
          - "empty"
          - "country_only"
          - "exact"
          - "ambiguous"
          - "non_latin_no_match"
          - "not_found"
        """
        if not query:
            return {"status": "empty"}

        # Sanitize input: remove brackets and control chars, strip
        clean = re.sub(r"[<>\"\'`]", "", query).strip()
        if not clean or len(clean) > 60:
            return {"status": "not_found"}

        norm_query = strip_accents(clean).lower().strip()
        raw_query = clean.lower()

        # 1. Country-only check
        country_data = self._country_index.get(norm_query) or self._country_index.get(raw_query)
        # If matches country, check whether user meant country vs a primary city
        if country_data:
            has_primary_city = (norm_query in self._primary_city_index or raw_query in self._primary_city_index)
            # If no city has this exact primary name (e.g. India, Indonesia, Russia, USA), treat as country-only
            if not has_primary_city:
                iso = country_data.get("iso", "")
                cname = country_data.get("name", "")
                flag = country_code_to_flag(iso)
                loc_display = f"{cname} {flag}".strip()
                match = LocationMatch(
                    city="",
                    country_name=cname,
                    country_code=iso,
                    location_display=loc_display,
                    population=0,
                )
                return {"status": "country_only", "match": match}

        # 2. Search city matches: prefer primary name matches first
        matched_cities = self._primary_city_index.get(norm_query) or self._primary_city_index.get(raw_query)

        # If no primary match, search alternate names
        if not matched_cities:
            matched_cities = self._alt_city_index.get(raw_query) or self._alt_city_index.get(norm_query)

        # If still not found, check if query contains comma, e.g. "Delhi, India" or "Springfield, US"
        if not matched_cities and ("," in clean or " - " in clean):
            parts = [p.strip() for p in re.split(r"[,–—\-]", clean) if p.strip()]
            if len(parts) >= 2:
                city_part = parts[0]
                country_part = parts[1]
                c_norm = strip_accents(city_part)
                candidates = (
                    self._primary_city_index.get(c_norm)
                    or self._primary_city_index.get(city_part.lower())
                    or self._alt_city_index.get(city_part.lower())
                    or self._alt_city_index.get(c_norm)
                )
                if candidates:
                    ctry_info = self._country_index.get(strip_accents(country_part)) or self._country_index.get(country_part.lower())
                    target_iso = ctry_info.get("iso") if ctry_info else country_part.upper()
                    matched_cities = [c for c in candidates if c.get("countrycode") == target_iso]

        if not matched_cities:
            # If query didn't match a city, but matched a country, fallback to country
            if country_data:
                iso = country_data.get("iso", "")
                cname = country_data.get("name", "")
                flag = country_code_to_flag(iso)
                loc_display = f"{cname} {flag}".strip()
                match = LocationMatch(
                    city="",
                    country_name=cname,
                    country_code=iso,
                    location_display=loc_display,
                    population=0,
                )
                return {"status": "country_only", "match": match}

            # Check if input was in Cyrillic or Persian/Arabic script
            if has_cyrillic_or_persian(clean):
                return {"status": "non_latin_no_match"}
            return {"status": "not_found"}

        # Deduplicate candidates by (city_name, country_code, admin1code) and sort by population descending
        unique_matches: Dict[str, Dict[str, Any]] = {}
        for c in matched_cities:
            cname = c.get("name", "")
            ccode = c.get("countrycode", "")
            admin1 = c.get("admin1code", "")
            key = f"{cname.lower()}_{ccode.lower()}_{admin1.lower()}"
            pop = int(c.get("population", 0) or 0)
            if key not in unique_matches or pop > int(unique_matches[key].get("population", 0) or 0):
                unique_matches[key] = c

        sorted_candidates = sorted(
            unique_matches.values(),
            key=lambda item: int(item.get("population", 0) or 0),
            reverse=True,
        )

        match_objects: List[LocationMatch] = []
        is_multiple = len(sorted_candidates) > 1
        for c in sorted_candidates[:5]:
            cname = c.get("name", "")
            ccode = c.get("countrycode", "")
            admin1 = c.get("admin1code", "")
            pop = int(c.get("population", 0) or 0)
            gid = c.get("geonameid")
            country_info = self.countries.get(ccode, {})
            country_name = country_info.get("name", ccode)
            flag = country_code_to_flag(ccode)
            if is_multiple and admin1 and admin1.isalpha():
                loc_display = f"{cname} ({admin1}), {country_name} {flag}".strip()
            else:
                loc_display = f"{cname}, {country_name} {flag}".strip()
            match_objects.append(
                LocationMatch(
                    city=cname,
                    country_name=country_name,
                    country_code=ccode,
                    location_display=loc_display,
                    population=pop,
                    geonameid=gid,
                )
            )

        if len(match_objects) == 1:
            return {"status": "exact", "match": match_objects[0]}

        return {"status": "ambiguous", "matches": match_objects}


_resolver: Optional[LocationResolver] = None


def get_location_resolver() -> LocationResolver:
    global _resolver
    if _resolver is None:
        _resolver = LocationResolver()
    return _resolver


def validate_location(query: str) -> Dict[str, Any]:
    """Helper entry point for validating user input location."""
    return get_location_resolver().resolve(query)
