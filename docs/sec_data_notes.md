# SEC data notes

This dataset is a single SEC company facts payload from `data/raw/sec/0000019617.json`.

## Top-level structure

The JSON root contains:
- `cik`: SEC CIK identifier
- `entityName`: company name
- `facts`: nested taxonomy facts

## Taxonomies and concepts

Under `facts`, there are several XBRL taxonomies:
- `dei`: entity-level facts such as share counts and public float
- `invest`: investment/market-related facts
- `srt`: stock repurchase / treasury-related facts
- `us-gaap`: the main U.S. GAAP financial concepts; this is the largest taxonomy and contains most accounting values
- `ffd`: filing/offer-related metrics
- `ecd`: executive compensation / compensation-related metrics

The most relevant accounting concepts in `us-gaap` include examples like:
- `NetIncomeLoss` (`Net Income (Loss) Attributable to Parent`)
- `Revenues` (`Revenues`)
- `Assets` (`Assets`)
- `StockholdersEquity` (`Stockholders' Equity Attributable to Parent`)
- plus many other balance-sheet and income-statement concepts such as `AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent`, `CashAndCashEquivalentsAtCarryingValue`, and `OperatingIncomeLoss`

Each concept is shaped like:
- `facts["us-gaap"][conceptName] = { label, description, units }`

The `units` object maps a unit code such as `USD` to a list of period/value rows.

## Fields per value row

Each value entry in a concept's `units[unit]` list contains the standard SEC XBRL fields, including:
- `start`: start date of the reporting period
- `end`: end date of the reporting period
- `val`: numeric value for the fact
- `accn`: SEC accession number for the filing
- `fy`: fiscal year
- `fp`: fiscal period (`FY`, `Q1`, `Q2`, etc.)
- `form`: filing form (`10-K`, `10-Q`)
- `filed`: filing date
- `frame`: XBRL context/frame label (for example `CY2007`, `CY2008Q2I`)

Example from `NetIncomeLoss`:
```json
{
  "start": "2007-01-01",
  "end": "2007-12-31",
  "val": 15365000000,
  "accn": "0000950123-10-016029",
  "fy": 2009,
  "fp": "FY",
  "form": "10-K",
  "filed": "2010-02-24",
  "frame": "CY2007"
}
```

Example from `Assets`:
```json
{
  "end": "2008-12-31",
  "val": 2175052000000,
  "accn": "0000950123-09-032832",
  "fy": 2009,
  "fp": "Q2",
  "form": "10-Q",
  "filed": "2009-08-10"
}
```

Notes:
- Not every value row includes every field. Point-in-time facts often omit `start`; some rows omit `frame`.
- `val` is the main numeric value to analyze; `accn`/`filed` tie the fact back to a specific filing.
- The table is effectively a long-form fact table keyed by concept name and unit.
