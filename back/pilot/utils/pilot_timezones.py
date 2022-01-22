from collections import namedtuple

from datetime import datetime
import pytz

DEFAULT_TIMEZONE = 'Europe/Paris'

Timezone = namedtuple('Timezone', ['name', 'label', 'utc_offset'])
timezones = []
excluded = ['GMT', 'UTC']
for timezone_name in pytz.common_timezones:
    if timezone_name in excluded:
        continue

    tz_info = pytz.timezone(timezone_name)
    utc_offset = datetime.now(tz_info).utcoffset()
    human_readable_offset = datetime.now(tz_info).strftime('%z')
    human_readable_offset = human_readable_offset[0:-2] + ':' + human_readable_offset[-2:]
    # city = timezone.rsplit('/', 1)[-1]
    timezone_label = f"[UTC{human_readable_offset}] {timezone_name}"
    timezones.append(Timezone(
        timezone_name,
        timezone_label,
        utc_offset
    ))

timezones.sort(key=lambda timezone: timezone.utc_offset)

PILOT_TIMEZONE_CHOICES = [timezone[0:2] for timezone in timezones]


