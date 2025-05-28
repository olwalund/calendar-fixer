import requests
import yaml
from pathlib import Path
import os
import re
from datetime import datetime
import pytz

def fix_ics_times(ics_content):
    """
    Konverterar alla DTSTART och DTEND i UTC (med Z) till svensk lokal tid med rätt sommar/vintertid.
    """

    def convert_utc_to_swe(match):
        utc_str = match.group(2)  # t.ex. 20230528T120000Z
        dt_utc = datetime.strptime(utc_str, "%Y%m%dT%H%M%SZ")
        dt_utc = pytz.utc.localize(dt_utc)
        swedish_tz = pytz.timezone("Europe/Stockholm")
        dt_local = dt_utc.astimezone(swedish_tz)
        # Returnera i samma format fast utan Z och tidszonsangivelse (lokal tid)
        return f"{match.group(1)}:{dt_local.strftime('%Y%m%dT%H%M%S')}"

    # Matcha DTSTART eller DTEND följt av tid i UTC (slutar med Z)
    pattern = re.compile(r"(DTSTART|DTEND):(\d{8}T\d{6}Z)")

    fixed_content = pattern.sub(convert_utc_to_swe, ics_content)
    return fixed_content

def main():
    print("Nuvarande katalog:", os.getcwd())
    with open("feeds.yaml", "r") as f:
        feeds = yaml.safe_load(f)

    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    for name, feed in feeds["calendars"].items():
        url = feed["url"]
        print(f"Hämtar {name} från {url}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            fixed = fix_ics_times(r.text)
            filepath = output_dir / f"{name}.ics"
            filepath.write_text(fixed, encoding="utf-8")
            print(f"✔️ Sparade fil: {filepath.resolve()}")
        except Exception as e:
            print(f"❌ Fel vid hämtning av {name}: {e}")

if __name__ == "__main__":
    main()
