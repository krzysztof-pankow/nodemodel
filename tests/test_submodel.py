from nodemodel.model import Model

def test_submodel():
    def z(a):
        return a

    def y(b):
        return b

    def x(c):
        return c

    def a(b):
        return b

    def b():
        return 1

    def c():
        return 1

    m = Model({"z":z,"y":y,"x":x,"a":a,"b":b,"c":c})
    assert m.compute({}) == {'b': 1, 'c': 1, 'y': 1, 'a': 1, 'x': 1, 'z': 1}
    m_sub = m.submodel(["z","y"])
    assert m_sub.compute({}) == {'b': 1, 'y': 1, 'a': 1, 'z': 1}
