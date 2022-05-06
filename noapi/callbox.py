"""
callbox.py
Callbox
Analogous to a Closure or Promise or something
"""


class Callbox:
    def __init__(self, fid):
        super().__init__()
        self._fid = fid
        self.on_return = lambda ret: None

    def _on_return(self, ret):
        self.on_return(ret)
