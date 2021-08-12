import datetime


def tt(func):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()

        result = func(*args, **kwargs)

        end = datetime.datetime.now()
        print('----time----')
        print(end - start)
        return result
    return wrapper

