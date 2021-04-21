import os
import re

class_list = [
    "<class 'django.db.models.query.QuerySet'>",
    "<class 'dict'>",
    "<class 'stock.models.Account'>",
    "<class 'pandas.core.series.Series'>",
    "<class 'pandas.core.series.DataFrame'>"
]

for cl in class_list:
    print(re.findall(".*\.(\w+)\.", cl.replace("'","."))[0])
