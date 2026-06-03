---
name: data-ingest
description: "Ingest, clean, and normalize crash and traffic safety datasets from USA, Canada, and England for use in collision risk analysis."
---

# Data Ingestion

Ingest, clean, and normalize crash and traffic safety datasets from USA, Canada, and England for use in collision risk analysis.

## Data Sources by Jurisdiction

### USA — NHTSA Sources
| Source | Content | Access | Format |
|---|-|-|-|
| **FARS** | Fatal crashes, vehicle, occupant, environment | NHTSA API, CSV | CSV |
| **NASS-CRS** | Non-fatal crashes with detailed crash reports | NHTSA API, CSV | CSV |
| **CISS** | ~8000 detailed crash reports | NHTSA website | CSV/PDF |
| **CMFwiki** | Crash modification factors | Web/API | Web |
| **GES** | National estimates of non-fatal injuries | NHTSA API | CSV |

### Canada — Transport Canada Sources
| Source | Content | Access | Format |
|---|-|-|-|
| **TC Transportation Statistics** | Annual crash stats by province | TC website | PDF/CSV |
| **CMFwiki Canada** | Canadian crash modification factors | Web/API | Web |
| **ICBC BC** | Detailed crash reports in BC | ICBC website | CSV |
| **SAAQ Quebec** | Quebec crash data | SAAQ website | CSV |

### England — DfT Sources
| Source | Content | Access | Format |
|---|-|-|-|
| **DfT Road Casualties GB** | All reported road casualties (RSM series) | DfT website | CSV |
| **JACArP** | Detailed crash reports with vehicle data | JACArP website | Web/CSV |
| **Highways England** | Motorway crash statistics | DfT website | CSV/PDF |

## Standard Data Schemas

### Crash Record
```json
{
  "crash_id": "string", "jurisdiction": "USA|Canada|England",
  "date": "ISO-8601", "time": "HH:MM:SS",
  "location": { "lat", "lon", "road_type", "road_name", "speed_limit_ms",
                 "number_of_lanes", "surface_type", "lighting" },
  "conflict_type": "crossing|merging|diverging|weaving|rear-end|sideswipe|right-angle|opposing-left-turn|unknown",
  "severity_level": "fatal|major_injury|minor_injury|property_damage|no_injury",
  "weather": "clear|rain|snow|fog|unknown",
  "road_geometry": { "intersection_type", "crossing_angle_deg", "curve_radius_m" },
  "vehicles": ["vehicle_records"], "pedestrians": ["occupant_records"],
  "cyclists": ["occupant_records"], "collision_detected": boolean,
  "collision_type": "collision|near_miss|unknown",
  "data_source": "string", "access_url": "string"
}
```

### Vehicle Record
```json
{
  "vehicle_id": "string", "vehicle_type": "sedan|suv|truck|heavy_truck|bus|motorcycle|other",
  "year": int, "make": "string", "model": "string", "mass_kg": float,
  "length_m": float, "width_m": float, "height_m": float, "color": "string",
  "speed_ms": float, "acceleration_ms2": float, "direction_deg": float,
  "occupant_count": int, "occupant_types": ["driver|front_passenger|..."],
  "impact_location": "front|rear|side|side_rear|roof|none",
  "seatbelt_used": boolean, "airbag_deployed": boolean, "abs_equipped": boolean,
  "autonomous_features": ["none|ldw|fcw|aeb|adaptive_cruise|lane_centering|other"]
}
```

## Ingestion Pipeline
```
[External Sources] → Ingestor/Loader → Normalizer → Validator → Storage
```

### Normalization Rules
- Speed conversion: mph × 0.44704, kph × 0.27778 → m/s
- Jurisdiction codes: US→USA, CA→Canada, GB→England
- Severity: US (1-4) → standard; DfT GB (1-3) → standard
- Conflict type mapping from source-specific codes

### Validation Rules
- Required fields: 100% completeness (crash_id, date, lat/lon)
- Optional fields: ≥ 80% completeness for statistical analysis
- Location data: ≥ 90% completeness (lat/lon)
- Vehicle data: ≥ 85% completeness
- Duplicate crash IDs: removed during dedup
- Date range: 1975–2026
- Coordinates: within jurisdiction boundaries
- Speeds: 0–100 m/s
- Masses: vehicle type limits

## Quality Metrics
- Required fields: 100% completeness
- Optional fields: ≥ 80% completeness
- Location data: ≥ 90% completeness
- Vehicle data: ≥ 85% completeness
- No duplicate records after dedup
- All dates within 1975–2026
- All coordinates within jurisdiction boundaries
- All speeds within 0–100 m/s
- All masses within vehicle type limits

## Documentation Required
Each dataset must include:
- Source URL and access date
- Number of records ingested
- Number of records after cleaning
- List of missing fields
- Known limitations

## Reuse Trigger

Use when:
- Loading any collision risk dataset
- Validating data quality before analysis
- Ingesting new data sources
- Standardizing cross-jurisdictional data

## File Structure
```
src/data_ingest/
├── ingestor.py        Main ingestion engine
├── loaders/           Per-source loaders (nhtsa_fars, nhtsa_ciss,
│                       transport_canada, icbc_bc, dtf_gb, jacarp)
├── normalizer.py       Field standardization
├── validator.py        Data validation rules
├── schemas/           Standard schemas (crash_record, vehicle_record)
└── raw/               Raw downloaded files (gitignored)
└── processed/         Cleaned and normalized data
```
