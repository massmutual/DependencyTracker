import pickle
from py4jdbc.utils import ShellPath

def test_ShellPath():
    mypath = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin"
    p = ShellPath(mypath)
    assert str(p) == mypath
    doogie = '/home/doogie/bin'
    p.append(doogie)
    assert doogie in p
    assert str(p).endswith(doogie)
    p.remove(doogie)
    assert doogie not in p
    assert doogie not in str(p)
    howser = '/opt/howser/bin'
    p.prepend(howser)
    assert howser in p
    assert str(p).startswith(howser)
    assert len(p) == mypath.count(':') + 2
    p.remove(howser)
    assert len(p) == mypath.count(':') + 1
    pkl = pickle.dumps(p)
    new_p = pickle.loads(pkl)
    assert str(p) == mypath
