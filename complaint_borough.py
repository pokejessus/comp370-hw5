import argparse
import csv
from datetime import datetime
from collections import defaultdict
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Output the number of each complaint type per borough"
    )
    parser.add_argument(
        '-i', '--input', required=True, help="Input CSV file"
    )
    parser.add_argument(
        '-s', '--start', required=True, help="Start date"
    )
    parser.add_argument(
        '-e', '--end', required=True, help="End date"
    )
    parser.add_argument(
        '-o', '--output', required=True, help="Output CSV file"
    )

    return parser.parse_args()


def parse_date(date_str):
    '''
    Attempt to parse date string across common NYC formats
    '''
    date_str = date_str.strip()
    if not date_str:
        return None

    formats=[
        "%m/%d/%Y %I:%M:%S %p",  # 01/01/2024 12:00:00 AM
        "%m/%d/%Y %H:%M:%S",     # 01/01/2024 00:00:00
        "%m/%d/%Y",              # 01/01/2024
        "%Y-%m-%d %H:%M:%S",     # 2024-01-01 00:00:00
        "%Y-%m-%d",              # 2024-01-01
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None



def main():
    args = parse_args()

    start_dt = parse_date(args.start)
    end_dt = parse_date(args.end)

    if not start_dt or not end_dt:
        print("Error, could not parse start or end date", file=sys.stderr)
        sys.exit(1)

    counts = defaultdict(int)

    with open(args.input, mode="r", encoding="utf-8", errors="ignore") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            created_str = row.get("Created Date", "")
            complaint_type = row.get("Complaint Type", "").strip()
            borough = row.get("Borough", "").strip()

            if not created_str or not complaint_type or not borough:
                continue

            row_dt = parse_date(created_str)
            if row_dt and start_dt <= row_dt <= end_dt:
                counts[(complaint_type, borough)] += 1

    # Open output stream (file or stdout)
    out_file = open(args.output, "w", newline="", encoding="utf-8") if args.output else sys.stdout

    try:
        writer = csv.writer(out_file)
        writer.writerow(["complaint type", "borough", "count"])

        for (complaint_type, borough), count in counts.items():
            writer.writerow([complaint_type, borough, count])
    finally:
        if args.output and out_file is not sys.stdout:
            out_file.close()


if __name__ == "__main__":
    main()