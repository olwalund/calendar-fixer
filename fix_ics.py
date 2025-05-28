import requests
import yaml
from pathlib import Path
import re
from datetime import datetime
import pytz

# Mappning MS tidszon -> IANA
WINDOWS_TO_IANA = {
    "Romance Standard Time": "Europe/Stockholm",
    "W. Europe Standard Time": "Europe/Stockholm",
    # Lägg till fler vid behov
}

def fix_ics_times(ics_content):
    # Byt ut Windows tidszon mot IANA
    for win_tz, iana_tz in WINDOWS_TO_IANA.items():
        ics_content = ics_content.replace(f"TZID={win_tz}", f"TZID={iana_tz}")

    # Regex för att hitta start- och sluttider med TZID
    dtstart_pattern = re.compile(r"(DTSTART;TZID=([^\:]+)):(\d{8}T\d{6})")
    dtend_pattern = re.compile(r"(DTEND;TZID=([^\:]+)):(\d{8}T\d{6})")

    def convert_match(match):
        full_key = match.group(1)  # t.ex. DTSTART;TZID=Europe/Stockholm
        tzname = match.group(2)    # t.ex. Europe/Stockholm
        dt_str = match.group(3)    # t.ex. 20250521T103000

        # Konvertera str till datetime
        dt = datetime.strptime(dt_str, "%Y%m%dT%H%M%S")

        try:
            tz = pytz.timezone(tzname)
        except Exception:
            # Om TZ inte finns, returnera originalet
            return match.group(0)

        dt_localized = tz.localize(dt)

        # Konvertera till UTC
        dt_utc = dt_localized.astimezone(pytz.utc)

        # Format UTC som Z-tid (UTC)
        dt_utc_str = dt_utc.strftime("%Y%m%dT%H%M%SZ")

        # Returnera som UTC-tid utan TZID
        # Exempel: DTSTART:20250521T083000Z
        key_simple = full_key.split(";")[0]  # DTSTART eller DTEND
        return f"{key_simple}:{dt_utc_str}"

    # Ersätt i hela ICS-innehållet
    ics_content = dtstart_pattern.sub(convert_match, ics_content)
    ics_content = dtend_pattern.sub(convert_match, ics_content)

    return ics_content

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
