# Skill: Data Ingestion

**Purpose:** Ingest, clean, and normalize crash and traffic safety datasets from USA, Canada, and England for use in collision risk analysis.

## 1. Data Sources by Jurisdiction

### 1.1 USA — NHTSA Sources

| Source | Content | Access | Format |
|---|-|-|-|
| **FARS** (Fatality Analysis Reporting System) | Fatal crashes, vehicle, occupant, environment details | NHTSA API, CSV download | CSV |
| **NASS-CRS** (National Automotive Sampling System - Crash Research System) | Non-fatal crashes with detailed crash reports | NHTSA API, CSV download | CSV |
| **CISS** (Crash Investigation Sampling System) | Detailed crash reports from ~8000 crashes | NHTSA website | CSV/PDF |
| **CMFwiki** (Clearinghouse for Mobility Factors) | Crash modification factors for various treatments | Web-based | Web/API |
| **GES** (General Estimates System) | National estimates of non-fatal injuries | NHTSA API | CSV |

### 1.2 Canada — Transport Canada Sources

| Source | Content | Access | Format |
|---|-|-|---|
| **Transport Canada Transportation Statistics** | Annual crash statistics by province | TC website | PDF/CSV |
| **CMFwiki Canada** | Canadian crash modification factors | Web-based | Web |
| **ICBC BC** (Insurance Corp of British Columbia) | Detailed crash reports in BC | ICBC website | CSV |
| **SAAQ Quebec** | Quebec crash data | SAAQ website | CSV |

### 1.3 England — DfT Sources

| Source | Content | Access | Format |
|---|-|-|-|
| **DfT Road Casualties Great Britain** | All reported road casualties (RSM series) | DfT website | CSV |
| **JACArP** (JCA Road Safety Database) | Detailed crash reports with vehicle data | JACArP website | Web/CSV |
| **Highways England** | Motorway crash statistics | DfT website | CSV/PDF |

## 2. Ingestion Pipeline Architecture

### 2.1 Data Flow

```
[External Sources]
    │
    ▼
┌──────────────┐
│   Ingestor   │  (downloads, parses, validates)
│   / Loader   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Normalizer │  (standardizes fields, units, jurisdiction codes)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Validator  │  (checks completeness, consistency, ranges)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Storage    │  (processed/ directory, database)
└──────────────┘
```

### 2.2 File Structure

```
src/data_ingest/
├── __init__.py
├── ingestor.py        — Main ingestion engine
├── loaders/
│   ├── __init__.py
│   ├── nhtsa_fars.py   — NHTSA FARS loader
│   ├── nhtsa_ciss.py   — NHTSA CISS loader
│   ├── nhtsa_ge_s.py   — NHTSA GES loader
│   ├── transport_canada.py — TC statistics loader
│   ├── icbc_bc.py      — ICBC BC loader
│   ├── saaq_quebec.py  — SAAQ Quebec loader
│   ├── dtf_gb.py       — DfT GB loader
│   └── jacarp.py       — JACArP loader
├── normalizer.py       — Field standardization
├── validator.py        — Data validation rules
├── schemas/
│   ├── crash_record.json   — Standard crash record schema
│   ├── vehicle_record.json — Standard vehicle record schema
│   └── occupant_record.json — Standard occupant record schema
└── raw/               — Raw downloaded files (gitignored)
└── processed/         — Cleaned and normalized data
```

## 3. Standard Data Schema

### 3.1 Crash Record Schema

```json
{
  "crash_id": "string",           // unique identifier
  "jurisdiction": "USA|Canada|England",
  "date": "ISO-8601",
  "time": "HH:MM:SS",
  "location": {
    "lat": float,
    "lon": float,
    "road_type": "urban|highway|freeway|intersection|other",
    "road_name": "string",
    "speed_limit_ms": float,
    "number_of_lanes": int,
    "surface_type": "dry|wet|snow|ice|gravel",
    "lighting": "day|dusk|night|dark_with_lights|dark_no_lights"
  },
  "conflict_type": "crossing|merging|diverging|weaving|rear-end|sideswipe|right-angle|opposing-left-turn|unknown",
  "severity_level": "fatal|major_injury|minor_injury|property_damage|no_injury",
  "weather": "clear|rain|snow|fog|unknown",
  "road_geometry": {
    "intersection_type": "standard|roundabout|signalized|unsignalized",
    "crossing_angle_deg": float,
    "curve_radius_m": float
  },
  "vehicles": ["vehicle_records"],
  "pedestrians": ["occupant_records"],
  "cyclists": ["occupant_records"],
  "collision_detected": boolean,
  "collision_type": "collision|near_miss|unknown",
  "data_source": "string",
  "access_url": "string"
}
```

### 3.2 Vehicle Record Schema

```json
{
  "vehicle_id": "string",
  "vehicle_type": "sedan|suv|truck|heavy_truck|bus|motorcycle|other",
  "year": int,
  "make": "string",
  "model": "string",
  "mass_kg": float,
  "length_m": float,
  "width_m": float,
  "height_m": float,
  "color": "string",
  "speed_ms": float,
  "acceleration_ms2": float,
  "direction_deg": float,
  "occupant_count": int,
  "occupant_types": ["driver|front_passenger|rear_passenger|unknown"],
  "impact_location": "front|rear|side|side_rear|roof|none",
  "seatbelt_used": boolean,
  "airbag_deployed": boolean,
  "abs_equipped": boolean,
  "autonomous_features": ["none|ldw|fcw|aeb|adaptive_cruise|lane_centering|other"]
}
```

## 4. Ingestion Process

### 4.1 Download Step

```python
class DataIngestor:
    def __init__(self):
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.loaders = {}
    
    def download_source(self, source: str, output_path: Path) -> bool:
        """Download data from a source."""
        loaders = {
            "fars": self._download_fars,
            "ciss": self._download_ciss,
            "ges": self._download_ges,
            "tc_stats": self._download_tc_stats,
            "icbc_bc": self._download_icbc,
            "saaq": self._download_saaq,
            "dtf_gb": self._download_dtf_gb,
            "jacarp": self._download_jacarp
        }
        
        loader = loaders.get(source)
        if not loader:
            raise ValueError(f"Unknown source: {source}")
        
        return loader(output_path)
    
    def _download_fars(self, path: Path) -> bool:
        """Download FARS data from NHTSA."""
        # NHTSA FARS provides annual CSV files
        # URL pattern: https://www.fars.nhtsa.dot.gov/...
        url = "https://www.fars.nhtsa.dot.gov/csv/fars_year.csv"
        # Handle authentication if needed
        return True
```

### 4.2 Parse Step

```python
def parse_fars_file(filepath: Path) -> List[dict]:
    """Parse NHTSA FARS CSV file into standard schema."""
    records = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {
                "crash_id": row["CRASH_NUM"],
                "jurisdiction": "USA",
                "date": parse_fars_date(row["CRASH_DATE"]),
                "location": {
                    "lat": float(row["LATITUDE"]),
                    "lon": float(row["LONGITUDE"]),
                    "road_type": map_fars_road_type(row["ROAD_CLASS"]),
                    "surface_type": map_fars_surface(row["ROAD_SURFACE"]),
                    "lighting": map_fars_lighting(row["LIGHT_CONDTN"])
                },
                "severity_level": map_fars_severity(row["INJURY_SEV"]),
                "vehicles": parse_fars_vehicles(row),
                "data_source": "NHTSA-FARS",
                "access_url": "https://fars.nhtsa.dot.gov/"
            }
            records.append(record)
    return records
```

### 4.3 Normalize Step

```python
class DataNormalizer:
    def normalize_crash_record(self, record: dict) -> dict:
        """Normalize a crash record to standard schema."""
        # Standardize jurisdiction codes
        record["jurisdiction"] = self.normalize_jurisdiction(record["jurisdiction"])
        
        # Standardize speed units (convert to m/s if needed)
        for vehicle in record["vehicles"]:
            vehicle["speed_ms"] = self.convert_to_ms(vehicle["speed"], vehicle.get("speed_unit", "ms"))
        
        # Standardize severity levels
        record["severity_level"] = self.normalize_severity(record["severity_level"])
        
        # Standardize conflict type
        record["conflict_type"] = self.normalize_conflict_type(record["conflict_type"])
        
        return record
    
    def normalize_jurisdiction(self, code: str) -> str:
        mapping = {
            "US": "USA", "USA": "USA", "U.S.": "USA",
            "CA": "Canada", "CAN": "Canada", "CA_Canada": "Canada",
            "GB": "England", "ENG": "England", "EGB": "England"
        }
        return mapping.get(code, code)
    
    def convert_to_ms(self, speed: float, unit: str) -> float:
        if unit in ["mph"]:
            return speed * 0.44704
        elif unit in ["kph", "kmh"]:
            return speed * 0.27778
        elif unit in ["ms", "m/s"]:
            return speed
        else:
            return speed  # Assume m/s if unknown
```

### 4.4 Validate Step

```python
class DataValidator:
    def validate_crash_record(self, record: dict) -> List[str]:
        """Validate a normalized crash record. Returns list of errors."""
        errors = []
        
        # Check required fields
        if not record.get("crash_id"):
            errors.append("Missing crash_id")
        
        if not record.get("date"):
            errors.append("Missing date")
        
        if not record.get("location", {}).get("lat"):
            errors.append("Missing latitude")
        
        if not record.get("location", {}).get("lon"):
            errors.append("Missing longitude")
        
        # Check value ranges
        if record["location"]["lat"] < -90 or record["location"]["lat"] > 90:
            errors.append(f"Invalid latitude: {record['location']['lat']}")
        
        if record["location"]["lon"] < -180 or record["location"]["lon"] > 180:
            errors.append(f"Invalid longitude: {record['location']['lon']}")
        
        # Check vehicle constraints
        for vehicle in record["vehicles"]:
            if vehicle["mass_kg"] < 500 or vehicle["mass_kg"] > 50000:
                errors.append(f"Invalid vehicle mass: {vehicle['mass_kg']}")
            
            if vehicle["speed_ms"] < 0 or vehicle["speed_ms"] > 100:
                errors.append(f"Invalid vehicle speed: {vehicle['speed_ms']}")
        
        return errors
```

## 5. Jurisdiction-Specific Mapping Rules

### 5.1 NHTSA FARS → Standard Schema

```python
FARS_MAPPING = {
    "CRASH_NUM": "crash_id",
    "CRASH_DATE": "date",
    "LATITUDE": "location.lat",
    "LONGITUDE": "location.lon",
    "ROAD_CLASS": {
        "1": "urban", "2": "rural_interstate", "3": "rural_other",
        "4": "urban_interstate", "5": "local_urban"
    },
    "ROAD_SURFACE": {
        "DRY": "dry", "WET": "wet", "SNOW": "snow", "ICE": "ice"
    },
    "LIGHT_CONDTN": {
        "DAYLIGHT": "day", "DARK-LIT": "night", "DARK-NOT-LIT": "dark_no_lights",
        "TWILIGHT": "dusk", "DARK-LIGHT-UNKNOWN": "night"
    },
    "INJURY_SEV": {
        "1": "fatal", "2": "major_injury", "3": "minor_injury",
        "4": "property_damage", "9": "unknown"
    },
    "INJURIES": "severity_count"
}
```

### 5.2 DfT GB → Standard Schema

```python
DTF_GB_MAPPING = {
    "ACCIDENT_INDEX": "crash_id",
    "DATE": "date",
    "TIME": "time",
    "EASTING": "location.lon",  # UK uses Eastings
    "NORTHING": "location.lat",  # UK uses Northings
    "ACCIDENT_SEVERITY": {
        "1": "fatal", "2": "serious", "3": "slight"
    },
    "VEHICLE_TYPE": {
        "1": "motorcycle", "2": "car", "3": "van", "4": "truck",
        "5": "bus", "6": "taxi", "7": "pedal_cycle"
    }
}
```

## 6. Data Quality Checks

### 6.1 Completeness

```python
def check_completeness(records: List[dict], required_fields: List[str]) -> dict:
    """Check completeness of dataset."""
    results = {}
    for field in required_fields:
        count = sum(1 for r in records if field in r and r[field] is not None)
        results[field] = {
            "count": count,
            "percentage": (count / len(records) * 100) if records else 0
        }
    return results
```

### 6.2 Consistency

```python
def check_consistency(records: List[dict]) -> List[str]:
    """Check for inconsistencies in the dataset."""
    issues = []
    
    # Check date ranges
    dates = [r["date"] for r in records if r.get("date")]
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        if (max_date - min_date).days > 365 * 10:
            issues.append(f"Unusual date range: {min_date} to {max_date}")
    
    # Check for duplicate crash IDs
    crash_ids = [r["crash_id"] for r in records]
    duplicates = [id for id in set(crash_ids) if crash_ids.count(id) > 1]
    if duplicates:
        issues.append(f"Found {len(duplicates)} duplicate crash IDs")
    
    return issues
```

### 6.3 Range Validation

```python
def check_ranges(records: List[dict]) -> List[str]:
    """Check for values outside physical ranges."""
    issues = []
    
    for record in records:
        for vehicle in record.get("vehicles", []):
            if vehicle.get("mass_kg", 0) < 500 or vehicle.get("mass_kg", 0) > 50000:
                issues.append(f"Invalid mass: {vehicle['mass_kg']} in {record['crash_id']}")
            
            if vehicle.get("speed_ms", 0) < 0 or vehicle.get("speed_ms", 0) > 100:
                issues.append(f"Invalid speed: {vehicle['speed_ms']} in {record['crash_id']}")
    
    return issues
```

## 7. Validation Requirements

### 7.1 Completeness Threshold
- **Required fields:** 100% completeness
- **Optional fields:** ≥ 80% completeness for statistical analysis
- **Location data:** ≥ 90% completeness (lat/lon)
- **Vehicle data:** ≥ 85% completeness

### 7.2 Quality Metrics
- **No duplicate records** after deduplication
- **All dates** within reasonable range (1975–2026)
- **All coordinates** within jurisdiction boundaries
- **All speeds** within physical limits (0–100 m/s)
- **All masses** within vehicle type limits

### 7.3 Documentation
Each dataset must include:
- Source URL and access date
- Number of records ingested
- Number of records after cleaning
- List of missing fields
- Known limitations
