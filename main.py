from noapi.noapi import register, info, call, run
from app.motor.motor import Motor
from time import sleep


@register('pything1')
def py_thing_1(data):
    return f'Data: {data}'


@register('pything2')
def py_thing_2(data):
    info('Start thing 2!')
    info(f'Waiting...')
    sleep(3)
    return f'Data: {data}'


def on_info(msg):
    print(f'INFO {msg}')


def js_thing_1(data):
    def on_ret(ret):
        print(f'jsThing1({data}) = {ret}')
    cb = call('jsthing1', data)
    cb.on_return = on_ret


def js_thing_2(data):
    def on_ret(ret):
        print(f'jsThing2({data}) = {ret}')
    cb = call('jsthing2', data)
    cb.on_return = on_ret


def main():
    print('Starting App...')

    server = run(80, './app/content')
    server.on_info = on_info
    server.run_forever()


if __name__ == '__main__':
    main()
