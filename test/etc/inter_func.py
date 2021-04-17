def main_fn(aaa):
    aaa = aaa
    def sub_fn():
        return aaa + 'ccc'

    print(sub_fn())


if __name__ == '__main__':
    main_fn('aaaa')