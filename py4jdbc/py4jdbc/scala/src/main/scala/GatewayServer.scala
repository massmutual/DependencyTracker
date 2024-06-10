/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// import java.net.URI
import java.sql.{ResultSet, ResultSetMetaData, Connection, Statement}

import scala.collection.mutable.ArrayBuffer
import scala.collection.JavaConversions._
import scala.collection.mutable
import scala.util.Failure
import scala.util.Try

import py4j.GatewayServer
import net.razorvine.pickle.{Unpickler, Pickler}


trait Py4jdbcResponse {
  private val pickler = new Pickler()

  def pySerialize[T](codeblock: => T): Array[Byte] = {
      pickler.dumps(codeblock)
  }
}



class PyResultSet(resultSet: ResultSet) extends Py4jdbcResponse {
  var st: Any = 0
  val rs: ResultSet = resultSet
  private var index: Int = 0

  // -------------------------------------------------------------------------
  // SQL functions.
  def colNames: Array[Byte] = {
    pySerialize {
      val md = rs.getMetaData
      val colNames = for (i <- 1 to md.getColumnCount) yield md.getColumnName(i)
      colNames.toArray
    }
  }

  def colLabels: Array[Byte] = {
    pySerialize {
      val md = rs.getMetaData
      val colNames = for (i <- 1 to md.getColumnCount) yield md.getColumnLabel(i)
      colNames.toArray
    }
  }

  def collect(n: Int = 0): Array[Object] = {
    var rows = new mutable.ListBuffer[Array[Object]]()
    if( n == 0) {
      while (rs.next()) {
        rows.append(resultSetToObjectArray(rs))
      }
      rows.toList.toArray
    } else {
      var i = 0
      while (i < n && rs.next()) {
        rows.append(resultSetToObjectArray(rs))
        i = i + 1
      }
      rows.toList.toArray
    }
  }

  def resultSetToObjectArray(rs: ResultSet): Array[Object] = {
    Array.tabulate[Object](rs.getMetaData.getColumnCount)(i => rs.getObject(i + 1))
  }

  def fetchOne: Array[Byte] = {
    pySerialize {
      if(rs.next()) {
        val row = resultSetToObjectArray(rs)
        row.toArray
      } else {
        null
      }
    }
  }

  def fetchMany(n: Int = 0): Array[Byte] = {
    pySerialize {
      collect(n)
    }
  }

  def fetchAll(): Array[Byte] = {
    pySerialize {
      collect(0)
    }
  }

  def getColDescription(col: Int): Array[Any] = {
    val meta = rs.getMetaData()
    val size = meta.getColumnDisplaySize(col)
    val coltype = meta.getColumnType(col)
    Array(
      meta.getColumnName(col),
      coltype,
      size,
      size,
      meta.getPrecision(col),
      meta.getScale(col),
      meta.isNullable(col))
  }

  def getDescription(): Array[Byte] = {
    pySerialize {
      var cols = new mutable.ListBuffer[Array[Object]]()
      val numcols = rs.getMetaData().getColumnCount()
      (1 to numcols).map(getColDescription).toArray
    }
  }

  def close(): Unit = {
    if (st != 0) {
      try {
        st.asInstanceOf[Statement].close()
      } catch {
          case e: Exception => println(e)
      }
    }
      try {
        rs.close()
      } catch {
          case e: Exception => println(e)
      }
  }
}


class Dbapi2Connection(jdbc_url: String, user: String, password: String) extends Py4jdbcResponse {
  @transient lazy val conn = java.sql.DriverManager.getConnection(jdbc_url, user, password)

  def getJdbcConnection: Connection = conn

  def executeQuery(sql: String): PyResultSet = {
    val stmt = conn.createStatement()
    stmt.executeQuery(sql)
    val rs = stmt.getResultSet()
    val pyrs = new PyResultSet(rs.asInstanceOf[ResultSet])
    pyrs.st = stmt
    pyrs
  }

  def execute(sql: String): PyResultSet = {
    val stmt = conn.createStatement()
    stmt.execute(sql)
    val rs = stmt.getResultSet()
    val pyrs = new PyResultSet(rs.asInstanceOf[ResultSet])
    pyrs.st = stmt
    pyrs
  }

  def execute(sql: String, parameters: java.util.ArrayList[Any]): PyResultSet = {
    val stmt = conn.prepareStatement(sql)
    val params = parameters.toArray().asInstanceOf[Array[Any]]
    ((1 to params.length) zip params).foreach { case (i, obj) => stmt.setObject(i, obj)}
    stmt.execute()
    val rs = stmt.getResultSet()
    val pyrs = new PyResultSet(rs.asInstanceOf[ResultSet])
    pyrs.st = stmt
    pyrs
  }

  def executeMany(sql: String, parameterSeq: java.util.ArrayList[java.util.ArrayList[Any]]): PyResultSet = {
    val stmt = conn.prepareStatement(sql)
    for (i <- 0 to parameterSeq.size() - 1) {
        val params = parameterSeq.get(i)
        for (j <- 0 to params.size() - 1) {
            stmt.setObject(j + 1, params.get(j))
            }
        stmt.addBatch
       }
    stmt.executeBatch()
    val rs = stmt.getResultSet()
    val pyrs = new PyResultSet(rs.asInstanceOf[ResultSet])
    pyrs.st = stmt
    pyrs
  }
}


class GatewayEntryPoint  {
  private val pickler = new Pickler()

  def mkPyResultSet(rs: Any): PyResultSet = {
    new PyResultSet(rs.asInstanceOf[ResultSet])
  }

  def getConnection(jdbc_url: String, user: String, password: String): Dbapi2Connection = {
    new Dbapi2Connection(jdbc_url, user, password)
  }

  def getExceptionData(exc: Exception): Array[Byte] = {
    val classlist = getSupers(exc.getClass).map(_.toString).toArray
    var data = List(
         exc.getMessage,
         formatStackTrace(exc),
         classlist)
    pickler.dumps(data.toArray)
  }

  def formatStackTrace(exc: Throwable): String = {
    val sw = new java.io.StringWriter
    val pw = new java.io.PrintWriter(sw)
    exc.printStackTrace(pw)
    sw.getBuffer.toString
  }

  def getSupers(cl: Class[_]): List[Class[_]] = {
      if (cl == null) Nil else cl :: getSupers(cl.getSuperclass)
  }

}


object Gateway {

  def main(args: Array[String]) {
    val port = args.lift(0).getOrElse[String]("0").toInt
    val gatewayServer = new py4j.GatewayServer(new GatewayEntryPoint, port)
    gatewayServer.start()
    println(gatewayServer.getListeningPort())
  }

}
