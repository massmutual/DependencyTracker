import pytest

from py4jdbc.dbapi2 import connect, Connection
from py4jdbc.resultset import ResultSet
from py4jdbc.exceptions.dbapi2 import Error


def test_connect(gateway):
    url = "jdbc:derby:memory:testdb;create=true"
    conn = connect(url, gateway=gateway)
    cur = conn.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert isinstance(rs, ResultSet)


def test_execute(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert isinstance(rs, ResultSet)


def test_execute_with_params(derby):
    derby.autocommit = False
    cur = derby.cursor()
    cur.execute("create schema x_with_params")
    cur.execute("create table x_with_params.cowtest(a int, b char(1))")
    # Verify table is empty.
    rows = cur.execute("select * from x_with_params.cowtest as r").fetchall()
    assert len(rows) == 0
    # Insert one with parameter binding..
    sql = "insert into x_with_params.cowtest (a, b) values (?, ?)"
    cur.execute(sql, (12, "m"))
    # Verify there's 1 row.
    rows = cur.execute("select * from x_with_params.cowtest as r").fetchall()
    assert len(rows) == 1
    # Insert a bunch.
    params = list(enumerate("thecowsaremooing"))
    cur.executemany(sql, params)
    rows = cur.execute("select * from x_with_params.cowtest as r").fetchall()
    assert len(rows) == len("thecowsaremooing") + 1
    derby.rollback()
    derby.autocommit = True


def test_fetchone(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert isinstance(rs.fetchone(), rs.Row)


def test_fetchmany(derby):
    '''Assert all rows of result set have the correct class.
    '''
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert all({isinstance(row, rs.Row) for row in rs.fetchmany(5)})


def test_fetchManyCount(derby):
    derby.autocommit = False
    cur = derby.cursor()
    cur.execute("create schema x_with_params")
    cur.execute("create table x_with_params.cowtest(a int, b char(1))")
    sql = "insert into x_with_params.cowtest (a, b) values (?, ?)"
    params = list(enumerate("thecowsaremooing"))
    cur.executemany(sql, params)
    rs = cur.execute("select a from x_with_params.cowtest")
    ress = []
    while True:
        x = rs.fetchmany(3)
        ress.append(x)
        if len(x) < 3:
            break
    derby.rollback()
    derby.autocommit = True
    assert sum(map(len, ress)) == len("thecowsaremooing")


def test_fetchall(derby):
    '''Assert all rows of result set have the correct class.
    '''
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert all({isinstance(row, rs.Row) for row in rs.fetchall()})


def test_Cursor__iter__(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert all({isinstance(row, rs.Row) for row in rs})


def test_Cursor__iter__(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    # Exhaust all rows.
    list(rs)
    assert rs.fetchone() == None


def test_close_and_execute(derby):
    cur = derby.cursor()
    cur.close()
    with pytest.raises(Error):
        cur.execute("select * from SYS.SYSTABLES")


def test_close_and_fetchone(derby):
    cur = derby.cursor()
    cur.execute("select * from SYS.SYSTABLES")
    cur.close()
    with pytest.raises(Error):
        cur.fetchone()


def test_close_twice(derby):
    cur = derby.cursor()
    cur.close()
    with pytest.raises(Error):
        cur.close()


