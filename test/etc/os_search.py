import platform

if 'Windows' in platform.platform():
    print('true')
else:
    print('false')
print(platform.platform())