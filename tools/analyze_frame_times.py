#!/usr/bin/env python3
"""Summarize frame presentation timestamps from a CSV file.

The CSV must contain a timestamp_s column with one row per distinct frame, in
presentation order, in seconds. This tool does not capture frames or establish
whether an emulator's reported frames are distinct gameplay updates.
"""
import argparse
import csv
import json
import math
from pathlib import Path


def analyze(timestamps, target_fps=60.0):
    if not math.isfinite(target_fps) or target_fps <= 0:
        raise ValueError('target FPS must be finite and positive')
    if len(timestamps) < 2:
        raise ValueError('at least two frame timestamps are required')
    if any(not math.isfinite(t) for t in timestamps):
        raise ValueError('timestamps must be finite')
    intervals = [b - a for a, b in zip(timestamps, timestamps[1:])]
    if any(d <= 0 or not math.isfinite(d) for d in intervals):
        raise ValueError('timestamps must be strictly increasing')
    duration = timestamps[-1] - timestamps[0]
    ordered = sorted(intervals)
    def percentile(p):
        return ordered[max(0, math.ceil(p * len(ordered)) - 1)] * 1000.0
    budget = 1.0 / target_fps
    # Allow 1 microsecond of timestamp rounding before classifying an interval.
    late = sum(d > budget + 0.000001 for d in intervals)
    return {
        'frames': len(timestamps), 'intervals': len(intervals),
        'duration_seconds': duration, 'target_fps': target_fps,
        'target_frame_ms': budget * 1000.0,
        'average_fps': len(intervals) / duration,
        'frame_ms_p50': percentile(.50), 'frame_ms_p95': percentile(.95),
        'frame_ms_p99': percentile(.99), 'frame_ms_max': max(intervals) * 1000.0,
        'intervals_over_budget': late,
        'percent_over_budget': 100.0 * late / len(intervals),
        'measurement_note': 'Based on supplied timestamps; capture validity and game speed require separate verification.'
    }


def read_csv(path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or 'timestamp_s' not in reader.fieldnames:
            raise ValueError('CSV must contain a timestamp_s column')
        values = []
        for line, row in enumerate(reader, start=2):
            try:
                values.append(float(row['timestamp_s']))
            except (ValueError, TypeError) as exc:
                raise ValueError(f'invalid timestamp on line {line}') from exc
        return values


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv', type=Path)
    p.add_argument('--target-fps', type=float, default=60.0)
    p.add_argument('--output', type=Path, help='optional JSON output path')
    args = p.parse_args()
    try:
        result = analyze(read_csv(args.csv), args.target_fps)
    except (ValueError, OSError) as exc:
        p.error(str(exc))
    report = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding='utf-8')
    else:
        print(report, end='')


if __name__ == '__main__':
    main()
