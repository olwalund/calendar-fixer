import requests
import yaml
from pathlib import Path
import re
from datetime import datetime
import pytz

WINDOWS_TO_IANA = {
    "Romance Standard Time": "Europe/Stockholm",
    "W. Europe Standard Time": "Europe/Stockholm",
}

def fix_ics_times(ics_content):
    # Regex som fångar DTSTART/DTEND med TZID och tid
    pattern = re.compile(r'(DTSTART|DTEND);TZID=([^:]+):(\d{8}T\d{6})')

    def repl(match):
        prop = match.group(1)  # DTSTART eller DTEND
        win_tz = match.group(2)  # ex "Romance Standard Time"
        dt_str = match.group(3)  # ex "20250521T103000"

        # Mappa Windows-tz till IANA
        iana_tz = WINDOWS_TO_IANA.get(win_tz)
        if not iana_tz:
            # Om ingen mapping, behåll orginal (kan ev logga varning)
            return match.group(0)

        # Skapa datetime-objekt
        dt = datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
        tz = pytz.timezone(iana_tz)
        dt_localized = tz.localize(dt)

        # Konvertera till UTC
        dt_utc = dt_localized.astimezone(pytz.utc)

        # Formatera om som UTC-tid med Z och utan TZID
        dt_utc_str = dt_utc.strftime("%Y%m%dT%H%M%SZ")
        return f"{prop}:{dt_utc_str}"

    # Använd regex substitution för hela innehållet
    fixed_content = pattern.sub(repl, ics_content)
    return fixed_content

def main():
    print("🚀 Startar")
    with open("feeds.yaml", "r") as f:
        feeds = yaml.safe_load(f)

    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    for name, feed in feeds["calendars"].items():
        url = feed["url"]
        print(f"🌐 Hämtar {name} från {url}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            print(f"📥 Statuskod: {r.status_code}")
            fixed = fix_ics_times(r.text)
            (output_dir / f"{name}.ics").write_text(fixed, encoding="utf-8")
            print(f"✅ Sparade docs/{name}.ics")
        except Exception as e:
            print(f"❌ Fel vid hämtning av {name}: {e}")

if __name__ == "__main__":
    main()
