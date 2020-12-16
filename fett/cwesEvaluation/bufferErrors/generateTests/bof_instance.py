import sys

class Attr():
    """
    A key/value pair representation
    """

    def __init__(self, attr, val):
        self.attr = attr
        self.val  = val

    def __str__(self):
        return f"[{self.attr} := {self.val}]"

    def __repr__(self):
        return str(self)

class BofInstance():
    """
    Lightweight representation of a FMJSON instance (or configuration).
    The primary use is to view an instance as a collection of `Attr`s.
    """

    # Initialize with fmjson files
    def __init__(self, model, inst):
        for v in inst:
            if v not in model['features']:
                continue

            ## The parent is the attribute "name"
            ## hence if a feature _has_ a parent, then
            ## it is the value.
            x = model['features'][v]['parent']
            if x == "BufferErrors_Test":
                # Make top level values attributes, rather than elements of a
                # "BufferErrors_Test" list
                setattr(self, v, inst[v])
            else:
                ## Skip non-top level features that are not selected
                if not inst[v]:
                    continue
                try:
                    v0 = getattr(self, x)
                    if type(v0) == list:
                        setattr(self,x,v0 + [v])
                    else:
                        setattr(self,x,[v0,v])
                except:
                    if x:
                        setattr(self, x, v)

    def __str__(self):
        return str(vars(self))

