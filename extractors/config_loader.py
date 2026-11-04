"""Load and validate config/companies.yml.  Requires: pip install pyyaml"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

CIK_RE = re.compile(r"^\d{10}$")
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


@dataclass(frozen=True)
class CikSpec:
    cik: str                       # always 10-digit, zero-padded string
    fiscal_year_from: int | None = None
    fiscal_year_to: int | None = None

    @property
    def facts_url(self) -> str:
        return FACTS_URL.format(cik=self.cik)


@dataclass(frozen=True)
class Company:
    entity_id: str
    name: str
    ticker: str | None
    reporting_currency: str
    ciks: tuple[CikSpec, ...]


def load_companies(path: str | Path = "config/companies.yml") -> list[Company]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    default_ccy = (raw.get("defaults") or {}).get("reporting_currency", "USD")

    companies: list[Company] = []
    seen: set[str] = set()
    for item in raw["companies"]:
        eid = item["entity_id"]
        if eid in seen:
            raise ValueError(f"Duplicate entity_id: {eid}")
        seen.add(eid)

        specs = []
        for c in item["ciks"]:
            cik = str(c["cik"]).strip()
            if cik.isdigit() and len(cik) < 10:        # tolerate unquoted/short CIKs
                cik = cik.zfill(10)
            if not CIK_RE.match(cik):
                raise ValueError(f"{eid}: invalid CIK {c['cik']!r}")
            specs.append(CikSpec(cik, c.get("fiscal_year_from"), c.get("fiscal_year_to")))

        companies.append(
            Company(
                entity_id=eid,
                name=item["name"],
                ticker=item.get("ticker"),
                reporting_currency=item.get("reporting_currency", default_ccy),
                ciks=tuple(specs),
            )
        )
    return companies


if __name__ == "__main__":
    for co in load_companies():
        for s in co.ciks:
            print(co.entity_id, s.cik, s.fiscal_year_from, s.fiscal_year_to, s.facts_url)