# Data Ingestion Implementation Details

## Standard Data Schemas (Full)

### Crash Record Schema (schemas/crash_record.json)
```json
{
  "crash_id": "string",           // unique identifier
  "jurisdiction": "USA|Canada|England",
  "date": "ISO-8601",
  "time": "HH:MM:SS",
  "location": {
    "lat": float, "lon": float,
    "road_type": "urban|highway|freeway|intersection|other",
    "road_name": "string", "speed_limit_ms": float,
    "number_of_lanes": int, "surface_type": "dry|wet|snow|ice|gravel",
    "lighting": "day|dusk|night|dark_with_lights|dark_no_lights"
  },
  "conflict_type": "crossing|merging|diverging|weaving|rear-end|sideswipe|right-angle|opposing-left-turn|unknown",
  "severity_level": "fatal|major_injury|minor_injury|property_damage|no_injury",
  "weather": "clear|rain|snow|fog|unknown",
  "road_geometry": {
    "intersection_type": "standard|roundabout|signalized|unsignalized",
    "crossing_angle_deg": float, "curve_radius_m": float
  },
  "vehicles": ["vehicle_records"], "pedestrians": ["occupant_records"],
  "cyclists": ["occupant_records"], "collision_detected": boolean,
  "collision_type": "collision|near_miss|unknown",
  "data_source": "string", "access_url": "string"
}
```

### Vehicle Record Schema (schemas/vehicle_record.json)
```json
{
  "vehicle_id": "string",
  "vehicle_type": "sedan|suv|truck|heavy_truck|bus|motorcycle|other",
  "year": int, "make": "string", "model": "string", "mass_kg": float,
  "length_m": float, "width_m": float, "height_m": float, "color": "string",
  "speed_ms": float, "acceleration_ms2": float, "direction_deg": float,
  "occupant_count": int, "occupant_types": ["driver|front_passenger|rear_passenger|unknown"],
  "impact_location": "front|rear|side|side_rear|roof|none",
  "seatbelt_used": boolean, "airbag_deployed": boolean, "abs_equipped": boolean,
  "autonomous_features": ["none|ldw|fcw|aeb|adaptive_cruise|lane_centering|other"]
}
```

## Ingestor Implementation

```python
class DataIngestor:
    def __init__(self):
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.loaders = {}
    
    def download_source(self, source: str, output_path: Path) -> bool:
        loaders = {
            "fars": self._download_fars, "ciss": self._download_ciss,
            "ges": self._download_ges, "tc_stats": self._download_tc_stats,
            "icbc_bc": self._download_icbc, "saaq": self._download_saaq,
            "dtf_gb": self._download_dtf_gb, "jacarp": self._download_jacarp
        }
        loader = loaders.get(source)
        if not loader: raise ValueError(f"Unknown source: {source}")
        return loader(output_path)
    
    def _download_fars(self, path: Path) -> bool:
        url = "https://www.fars.nhtsa.dot.gov/csv/fars_year.csv"
        # Handle authentication if needed
        return True
```

## FARS Parser

```python
def parse_fars_file(filepath: Path) -> List[dict]:
    records = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {
                "crash_id": row["CRASH_NUM"],
                "jurisdiction": "USA",
                "date": parse_fars_date(row["CRASH_DATE"]),
                "location": {
                    "lat": float(row["LATITUDE"]), "lon": float(row["LONGITUDE"]),
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

## Normalizer Implementation

```python
class DataNormalizer:
    def normalize_crash_record(self, record: dict) -> dict:
        record["jurisdiction"] = self.normalize_jurisdiction(record["jurisdiction"])
        for vehicle in record["vehicles"]:
            vehicle["speed_ms"] = self.convert_to_ms(
                vehicle["speed"], vehicle.get("speed_unit", "ms"))
        record["severity_level"] = self.normalize_severity(record["severity_level"])
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
        if unit in ["mph"]: return speed * 0.44704
        elif unit in ["kph", "kmh"]: return speed * 0.27778
        elif unit in ["ms", "m/s"]: return speed
        else: return speed  # Assume m/s if unknown
```

## Validator Implementation

```python
class DataValidator:
    def validate_crash_record(self, record: dict) -> List[str]:
        errors = []
        if not record.get("crash_id"): errors.append("Missing crash_id")
        if not record.get("date"): errors.append("Missing date")
        if not record.get("location", {}).get("lat"): errors.append("Missing latitude")
        if not record.get("location", {}).get("lon"): errors.append("Missing longitude")
        if record["location"]["lat"] < -90 or record["location"]["lat"] > 90:
            errors.append(f"Invalid latitude: {record['location']['lat']}")
        if record["location"]["lon"] < -180 or record["location"]["lon"] > 180:
            errors.append(f"Invalid longitude: {record['location']['lon']}")
        for vehicle in record["vehicles"]:
            if vehicle["mass_kg"] < 500 or vehicle["mass_kg"] > 50000:
                errors.append(f"Invalid vehicle mass: {vehicle['mass_kg']}")
            if vehicle["speed_ms"] < 0 or vehicle["speed_ms"] > 100:
                errors.append(f"Invalid vehicle speed: {vehicle['speed_ms']}")
        return errors
    
    def check_completeness(records: List[dict], required_fields: List[str]) -> dict:
        results = {}
        for field in required_fields:
            count = sum(1 for r in records if field in r and r[field] is not None)
            results[field] = {"count": count, "percentage": (count / len(records) * 100) if records else 0}
        return results
    
    def check_consistency(records: List[dict]) -> List[str]:
        issues = []
        dates = [r["date"] for r in records if r.get("date")]
        if dates:
            min_date, max_date = min(dates), max(dates)
            if (max_date - min_date).days > 365 * 10:
                issues.append(f"Unusual date range: {min_date} to {max_date}")
        crash_ids = [r["crash_id"] for r in records]
        duplicates = [id for id in set(crash_ids) if crash_ids.count(id) > 1]
        if duplicates: issues.append(f"Found {len(duplicates)} duplicate crash IDs")
        return issues
    
    def check_ranges(records: List[dict]) -> List[str]:
        issues = []
        for record in records:
            for vehicle in record.get("vehicles", []):
                if vehicle.get("mass_kg", 0) < 500 or vehicle.get("mass_kg", 0) > 50000:
                    issues.append(f"Invalid mass: {vehicle['mass_kg']} in {record['crash_id']}")
                if vehicle.get("speed_ms", 0) < 0 or vehicle.get("speed_ms", 0) > 100:
                    issues.append(f"Invalid speed: {vehicle['speed_ms']} in {record['crash_id']}")
        return issues
```

## Jurisdiction-Specific Mapping Rules

### NHTSA FARS → Standard Schema
```python
FARS_MAPPING = {
    "CRASH_NUM": "crash_id", "CRASH_DATE": "date",
    "LATITUDE": "location.lat", "LONGITUDE": "location.lon",
    "ROAD_CLASS": {"1": "urban", "2": "rural_interstate", "3": "rural_other",
                   "4": "urban_interstate", "5": "local_urban"},
    "ROAD_SURFACE": {"DRY": "dry", "WET": "wet", "SNOW": "snow", "ICE": "ice"},
    "LIGHT_CONDTN": {"DAYLIGHT": "day", "DARK-LIT": "night", "DARK-NOT-LIT": "dark_no_lights",
                     "TWILIGHT": "dusk", "DARK-LIGHT-UNKNOWN": "night"},
    "INJURY_SEV": {"1": "fatal", "2": "major_injury", "3": "minor_injury",
                   "4": "property_damage", "9": "unknown"},
    "INJURIES": "severity_count"
}
```

### DfT GB → Standard Schema
```python
DTF_GB_MAPPING = {
    "ACCIDENT_INDEX": "crash_id", "DATE": "date", "TIME": "time",
    "EASTING": "location.lon", "NORTHING": "location.lat",  # UK uses Eastings/Northings
    "ACCIDENT_SEVERITY": {"1": "fatal", "2": "serious", "3": "slight"},
    "VEHICLE_TYPE": {"1": "motorcycle", "2": "car", "3": "van", "4": "truck",
                     "5": "bus", "6": "taxi", "7": "pedal_cycle"}
}
```
