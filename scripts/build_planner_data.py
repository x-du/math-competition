#!/usr/bin/env python3
"""Validate and publish event metadata independently of historical student results."""
import argparse
import csv
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'database/competition_events.json'
OUTPUT = ROOT / 'docs/competition_events.json'


def validate(data):
    assert data['schemaVersion'] == 1, 'Unsupported catalog schema'
    date.fromisoformat(data['updatedOn'])
    known = {r['folder_name'] for r in csv.DictReader((ROOT / 'database/contests/contests.csv').open())}
    covered, ids = set(), set()
    assert data['events'], 'Empty catalog'
    for event in data['events']:
        label = event['id']
        assert label not in ids and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label), f'Invalid/duplicate ID: {label}'
        ids.add(label)
        assert event['name'] and event['grades'] and event['notes'], label
        assert event['mode'] in ('campus', 'local'), label
        assert event['dateKind'] in ('fixed', 'window', 'unannounced'), label
        assert bool(event['startDate']) == (event['dateKind'] != 'unannounced'), label
        assert bool(event['endDate']) == bool(event['startDate']), label
        if event['startDate']:
            assert date.fromisoformat(event['startDate']) <= date.fromisoformat(event['endDate']), label
        if event['registrationDeadline']:
            deadline = date.fromisoformat(event['registrationDeadline'])
            if event['startDate']:
                assert deadline <= date.fromisoformat(event['startDate']), label
        if 'inDatabase' in event:
            assert isinstance(event['inDatabase'], bool), label
        if 'dateTentative' in event:
            assert isinstance(event['dateTentative'], bool) and event['startDate'], label
        if 'registrationNote' in event:
            assert isinstance(event['registrationNote'], str), label
        if event['checkedOn']:
            assert date.fromisoformat(event['checkedOn']) <= date.fromisoformat(data['updatedOn']), label
        assert event['sources'], label
        for url in [event['url'], *event['sources']]:
            parsed = urlparse(url)
            assert parsed.scheme == 'https' and parsed.netloc and not any(c in url for c in '\r\n'), label
        assert set(event['recordSlugs']) <= known, f'Unknown result slug: {label}'
        covered.update(event['recordSlugs'])
        location = event['location']
        assert (location is not None) == (event['mode'] == 'campus'), label
        if location:
            assert -90 <= location['lat'] <= 90 and -180 <= location['lng'] <= 180, label
            assert location['venue'] and location['city'], label
            assert location['precision'] in ('campus', 'previous-campus', 'city', 'previous-city'), label
    excluded = set(data.get('excludedOnlineRecordSlugs', []))
    assert excluded <= known and not excluded & covered, 'Invalid online-only exclusions'
    assert covered | excluded == known, f'Result competitions missing from catalog: {known - covered - excluded}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check generated output without writing')
    args = parser.parse_args()
    data = json.loads(SOURCE.read_text())
    validate(data)
    output = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
    if args.check:
        assert OUTPUT.read_text() == output, 'Run python3 scripts/build_planner_data.py to refresh output'
    else:
        OUTPUT.write_text(output)
    print(f'Validated {len(data["events"])} planner entries; result competitions covered or explicitly excluded as online-only.')


if __name__ == '__main__':
    main()
