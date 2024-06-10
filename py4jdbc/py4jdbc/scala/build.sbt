name := "py4jdbc"

version := "0.1.6.8"

crossScalaVersions := Seq("2.10.7", "2.11.12", "2.12.4")

scalaSource in Compile := baseDirectory.value / "src"

libraryDependencies ++= Seq(
    "net.sf.py4j" % "py4j" % "0.9",
    "org.spark-project" % "pyrolite" % "2.0",
    "org.apache.derby" % "derby" % "10.9.1.0",
    "org.postgresql" % "postgresql" % "9.4-1206-jdbc4"
    )
