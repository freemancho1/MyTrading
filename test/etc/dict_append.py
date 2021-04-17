aaa = {
    'aaaa': 'aaaa',
    'bbbb': 'bbbb',
}

aaa['cccc'] = aaa.get('cccc', 'cccc')
print(aaa['cccc'])

bbb = aaa['cccc']


print(f'aaa: {aaa}, {type(aaa)}')
print(f'bbb: {bbb}, {type(bbb)}')
print(f'aaa: {aaa}')

ccc = aaa.items()
# ddd = ccc['aaa', 'bbb']
print(f'ccc: {ccc}, {type(ccc)}')
# print(f'ddd: {ddd}, {type(ddd)}')
print(ccc.isdisjoint('dddd'))