"""Generer syntetiske KI-profiler. Kjør fra hvor som helst med repoets Python."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.kunstpixel.hr_simulator.ai_data import DATA_DIR, generate_dataset


def main() -> None:
    with (DATA_DIR / 'staff_source.csv').open(encoding='utf-8-sig', newline='') as handle:
        dataset = generate_dataset(list(csv.DictReader(handle)))
    (DATA_DIR / 'ai_profiles.json').write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    profiles = dataset['profiles']
    with (DATA_DIR / 'ai_profiles.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(profiles[0]))
        writer.writeheader()
        for profile in profiles:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, list) else value
                             for key, value in profile.items()})
    print(f"Generert {len(profiles)} syntetiske profiler i {DATA_DIR}")


if __name__ == '__main__':
    main()
