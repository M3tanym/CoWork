from time import sleep


class Motor:
    def __init__(self):
        self._pos = 0

    def _get_position(self):
        return self._pos

    def move(self, distance=1):
        target = self._pos + distance
        step = 1 if distance > 0 else -1
        while self._pos != target:
            self._pos += step
            sleep(0.1)

    position = property(_get_position)
