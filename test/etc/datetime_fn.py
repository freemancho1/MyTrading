from datetime import datetime, timedelta
from dateutil.parser import parse


first_day = parse('20210405').date()
sec_day = parse('20210412').date()
print(first_day)

print(type(first_day))
print((sec_day - first_day).days)