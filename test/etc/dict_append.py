import pandas as pd


names = ['Cho', 'Hong', 'Park', 'Kim', 'Song']
ages = [22, 33, 23, 45, 15]
checked = [True, False, False, True, False]

data_dt = dict(zip(names, ages))
print(data_dt)

account_dt = {
    'id': None,
    'acc_name': 'dddd',
    't_type': 'aaaa',
    't_count': 3,
    'base_money': 2000000,
}

series = pd.Series(account_dt)
print(type(series), '\n', series)
