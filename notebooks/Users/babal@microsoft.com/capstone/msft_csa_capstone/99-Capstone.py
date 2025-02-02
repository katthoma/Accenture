# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Databricks Partner Capstone Project
# MAGIC 
# MAGIC This optional capstone is included in the course to help you solidify key topics related to Databricks, Structured Streaming, and Delta.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC 
# MAGIC # Capstone Overview
# MAGIC 
# MAGIC In this project you will build a Delta Lake over incoming Streaming Data by using a series of Bronze, Silver, and Gold Tables. 
# MAGIC 
# MAGIC The Goal of the project is to gain actionable insights from a data lake, using a series of connected tables that: 
# MAGIC * Preserve the raw data
# MAGIC * Enrich the data by joining with additional static table
# MAGIC * Use Structured Streaming along with Delta tables to guarantee a robust solution
# MAGIC 
# MAGIC ## Scenario:
# MAGIC 
# MAGIC A video gaming company stores historical data in a data lake, which is growing exponentially. 
# MAGIC 
# MAGIC The data isn't sorted in any particular way (actually, it's quite a mess) and it is proving to be _very_ difficult to query and manage this data because there is so much of it.
# MAGIC 
# MAGIC Your goal is to create a Delta pipeline to work with this data. The final result is an aggregate view of the number of active users by week for company executives. You will:
# MAGIC * Create a streaming Bronze table by streaming from a source of files
# MAGIC * Create a streaming Silver table by enriching the Bronze table with static data
# MAGIC * Create a streaming Gold table by aggregating results into the count of weekly active users by week
# MAGIC * Visualize the results directly in the notebook
# MAGIC 
# MAGIC ## Testing your Code
# MAGIC There are 4 test functions imported into this notebook:
# MAGIC * realityCheckBronze
# MAGIC * realityCheckStatic
# MAGIC * realityCheckSilver
# MAGIC * realityCheckGold
# MAGIC 
# MAGIC To run automated tests against your code, you will call a realityCheck function and pass the function you write as an argument. The testing suite will call your functions against a different dataset so it's important that you don't change the parameters in the function definitions. 
# MAGIC 
# MAGIC To test your code yourself, simply call your function, passing the correct arugments. 
# MAGIC 
# MAGIC <img alt="Side Note" title="Side Note" style="vertical-align: text-bottom; position: relative; height:1.75em; top:0.05em; transform:rotate(15deg)" src="https://files.training.databricks.com/static/images/icon-note.webp"/> Calling your functions will start a stream. Streams can take around 30 seconds to start so the tests may take up to one minute to run as it has to wait for the stream you define to start. 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Getting Started
# MAGIC 
# MAGIC Run the following cell to configure our environment.

# COMMAND ----------

# MAGIC %run "./Includes/Capstone-Setup"

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Configure shuffle partitions
# MAGIC 
# MAGIC In order to speed up shuffle operations required by the solutions, let's update the number of shuffle partitions to 8 partitions. 

# COMMAND ----------

sqlContext.setConf("spark.sql.shuffle.partitions", "8")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC 
# MAGIC ### Set up paths
# MAGIC 
# MAGIC The cell below sets up relevant paths in DBFS.
# MAGIC 
# MAGIC <img alt="Side Note" title="Side Note" style="vertical-align: text-bottom; position: relative; height:1.75em; top:0.05em; transform:rotate(15deg)" src="https://files.training.databricks.com/static/images/icon-note.webp"/> It also clears out this directory (to ensure consistent results if re-run). This operation can take several minutes.

# COMMAND ----------

inputPath = "/mnt/training/gaming_data/mobile_streaming_events"

basePath = userhome + "/capstone"
outputPathBronze = basePath + "/gaming/bronze"
outputPathSilver = basePath + "/gaming/silver"
outputPathGold   = basePath + "/gaming/gold"

dbutils.fs.rm(basePath, True)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### SQL Table Setup
# MAGIC 
# MAGIC The follow cell drops a table that we'll be creating later in the notebook.
# MAGIC 
# MAGIC (Dropping the table prevents challenges involved if the notebook is run more than once.)

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS mobile_events_delta_gold;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 1: Prepare Schema and Read Streaming Data from input source
# MAGIC 
# MAGIC The input source is a folder containing 20 files of around 50 MB each. 
# MAGIC 
# MAGIC The stream defined below is configured to read one file per trigger. 
# MAGIC 
# MAGIC Run this code to start the streaming read from the file directory. 

# COMMAND ----------

from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType, DoubleType

eventSchema = ( StructType()
  .add('eventName', StringType()) 
  .add('eventParams', StructType() 
    .add('game_keyword', StringType()) 
    .add('app_name', StringType()) 
    .add('scoreAdjustment', IntegerType()) 
    .add('platform', StringType()) 
    .add('app_version', StringType()) 
    .add('device_id', StringType()) 
    .add('client_event_time', TimestampType()) 
    .add('amount', DoubleType()) 
  )     
)

gamingEventDF = (spark
  .readStream
  .schema(eventSchema) 
  .option('streamName','mobilestreaming_demo') 
  .option("maxFilesPerTrigger", 1)                # treat each file as Trigger event
  .json(inputPath) 
)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### Step 2: Write Stream to Bronze Table
# MAGIC 
# MAGIC Complete the `writeToBronze` function to perform the following tasks:
# MAGIC 
# MAGIC * Write the stream from `gamingEventDF` -- the stream defined above -- to a bronze Delta table in path defined by `outputPathBronze`.
# MAGIC * Convert the input column `client_event_time` to a date format and rename the column to `eventDate`
# MAGIC * Filter out records with a null value in the `eventDate` column
# MAGIC * Make sure you provide a checkpoint directory that is unique to this stream
# MAGIC 
# MAGIC <img alt="Side Note" title="Side Note" style="vertical-align: text-bottom; position: relative; height:1.75em; top:0.05em; transform:rotate(15deg)" src="https://files.training.databricks.com/static/images/icon-note.webp"/> Using `append` mode when streaming allows us to insert data indefinitely without rewriting already processed data.

# COMMAND ----------

# TODO

from pyspark.sql.functions import col, to_date

def writeToBronze(sourceDataframe, bronzePath, streamName):
  (sourceDataframe
    .withColumn("eventDate", (col("eventParams.client_event_time").cast("date")))
    .filter(col("eventParams.client_event_time").isNotNull())
    .writeStream
    .format("delta")       
    .option("checkpointLocation", bronzePath + "/_checkpoint")
    .queryName(streamName)
    .outputMode("append") 
    .start(bronzePath)
  )

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Call your writeToBronze function
# MAGIC 
# MAGIC To start the stream, call your `writeToBronze` function in the cell below.

# COMMAND ----------

writeToBronze(gamingEventDF, outputPathBronze, "bronze_stream")

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Check your answer 
# MAGIC 
# MAGIC Call the realityCheckBronze function with your writeToBronze function as an argument.

# COMMAND ----------

realityCheckBronze(writeToBronze)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3a: Load static data for enrichment
# MAGIC 
# MAGIC Complete the `loadStaticData` function to perform the following tasks:
# MAGIC 
# MAGIC * Register a static lookup table to associate `deviceId` with `deviceType` (android or ios).
# MAGIC * While we refer to this as a lookup table, here we'll define it as a DataFrame. This will make it easier for us to define a join on our streaming data in the next step.
# MAGIC * Create `deviceLookupDF` by calling your loadStaticData function, passing `/mnt/training/gaming_data/dimensionData` as the path.

# COMMAND ----------

# TODO
lookupPath = "/mnt/training/gaming_data/dimensionData"

def loadStaticData(path):
  return spark.read.format("delta").load(path)

deviceLookupDF = loadStaticData(lookupPath)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ##Check your answer
# MAGIC 
# MAGIC Call the reaityCheckStatic function, passing your loadStaticData function as an argument. 

# COMMAND ----------

realityCheckStatic(loadStaticData)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### Step 3b: Create a streaming silver Delta table
# MAGIC 
# MAGIC A silver table is a table that combines, improves, or enriches bronze data. 
# MAGIC 
# MAGIC In this case we will join the bronze streaming data with some static data to add useful information. 
# MAGIC 
# MAGIC #### Steps to complete
# MAGIC 
# MAGIC Complete the `bronzeToSilver` function to perform the following tasks:
# MAGIC * Create a new stream by joining `deviceLookupDF` with the bronze table stored at `outputPathBronze` on `deviceId`.
# MAGIC * Make sure you do a streaming read and write
# MAGIC * Your selected fields should be:
# MAGIC   - `device_id`
# MAGIC   - `eventName`
# MAGIC   - `client_event_time`
# MAGIC   - `eventDate`
# MAGIC   - `deviceType`
# MAGIC * **NOTE**: some of these fields are nested; alias them to end up with a flat schema
# MAGIC * Write to `outputPathSilver`
# MAGIC 
# MAGIC <img alt="Caution" title="Caution" style="vertical-align: text-bottom; position: relative; height:1.3em; top:0.0em" src="https://files.training.databricks.com/static/images/icon-warning.svg"/> Don't forget to checkpoint your stream!

# COMMAND ----------

# TODO

from pyspark.sql.functions import col

def bronzeToSilver(bronzePath, silverPath, streamName, lookupDF):
  (spark.readStream
    .format("delta")
    .load(bronzePath)
    .join(lookupDF,col("eventParams.device_id") == col("device_id"))
    .select(col("eventParams.device_id"),col("eventName"),col("eventParams.client_event_time"),col("eventDate"),col("deviceType"))
    .writeStream 
    .format("delta")
    .option("checkpointLocation", silverPath + "/_checkpoint")
    .queryName(streamName)
    .outputMode("append")
    .start(silverPath))

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Call your bronzeToSilver function
# MAGIC 
# MAGIC To start the stream, call your `bronzeToSilver` function in the cell below.

# COMMAND ----------

bronzeToSilver(outputPathBronze, outputPathSilver, "silver_stream", deviceLookupDF)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Check your answer 
# MAGIC 
# MAGIC Call the realityCheckSilver function with your bronzeToSilver function as an argument.

# COMMAND ----------

realityCheckSilver(bronzeToSilver)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4a: Batch Process a Gold Table from the Silver Table
# MAGIC 
# MAGIC The company executives want to look at the number of active users by week. They use SQL so our target will be a SQL table backed by a Delta Lake. 
# MAGIC 
# MAGIC The table should have the following columns:
# MAGIC - `WAU`: count of weekly active users (distinct device IDs grouped by week)
# MAGIC - `week`: week of year (the appropriate SQL function has been imported for you)
# MAGIC 
# MAGIC In the first step, calculate these 

# COMMAND ----------

# TODO

from pyspark.sql.functions import weekofyear

def silverToGold(silverPath, goldPath, queryName):
    (    spark.readStream.format("delta").load(silverPath).groupBy(weekofyear("eventDate"))
   .agg(F.min(weekofyear("eventDate")).alias("week"),F.approx_count_distinct("device_id").alias("WAU"),F.min("client_event_time").alias("client_event_time"))
   .select("week","WAU","client_event_time")
   .withWatermark("client_event_time", "1 hours")
   .writeStream.format("delta")
   .option("checkpointLocation", goldPath + "/_checkpoint")
   .outputMode("complete")
   .start(goldPath)
  )

# COMMAND ----------

# TODO - do not use
from pyspark.sql.functions import weekofyear

def silverToGold(silverPath, goldPath, queryName):
  inputdf = (
      spark.readStream.format("delta").load(silverPath)
  )
  aggrdf = (inputdf.groupBy(weekofyear("client_event_time"))
                .agg(F.min(weekofyear("client_event_time")).alias("week"),F.count("device_id").alias("WAU"),F.min("client_event_time").alias("client_event_time"))
            .select("week","WAU","client_event_time")
            .withWatermark("client_event_time", "1 hours")
           )
  writedf = (aggrdf.select("week","WAU"))
  
  writedf.writeStream.format("delta").option("checkpointLocation", goldPath + "/_checkpoint").outputMode("complete").start(goldPath)
  
  #spark.sql("CREATE TABLE IF NOT EXISTS mobile_events_delta_silver (WAU INT, week INT) USING DELTA LOCATION '" + goldPath + "'")

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Call your silverToGold function
# MAGIC 
# MAGIC To start the stream, call your `silverToGold` function in the cell below.

# COMMAND ----------

silverToGold(outputPathSilver, outputPathGold, "gold_stream")

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ##Check your answer
# MAGIC 
# MAGIC Call the reaityCheckGold function, passing your silverToGold function as an argument. 

# COMMAND ----------

realityCheckGold(silverToGold)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC 
# MAGIC ### Step 4b: Register Gold SQL Table
# MAGIC 
# MAGIC By linking the Spark SQL table with the Delta Lake file path, we will always get results from the most current valid version of the streaming table.
# MAGIC 
# MAGIC <img alt="Side Note" title="Side Note" style="vertical-align: text-bottom; position: relative; height:1.75em; top:0.05em; transform:rotate(15deg)" src="https://files.training.databricks.com/static/images/icon-note.webp"/> It may take some time for the previous streaming operations to start. 
# MAGIC 
# MAGIC Once they have started register a SQL table against the gold Delta Lake path. 
# MAGIC 
# MAGIC * tablename: `mobile_events_delta_gold`
# MAGIC * table Location: `outputPathGold`

# COMMAND ----------

# TODO
spark.sql("""
   CREATE TABLE IF NOT EXISTS mobile_events_delta_silver
   FILL_IN
  """.format(outputPathGold))

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### Step 4c: Visualization
# MAGIC 
# MAGIC The company executives are visual people: they like pretty charts.
# MAGIC 
# MAGIC Create a bar chart out of `mobile_events_delta_gold` where the horizontal axis is month and the vertical axis is WAU.
# MAGIC 
# MAGIC Under <b>Plot Options</b>, use the following:
# MAGIC * <b>Keys:</b> `week`
# MAGIC * <b>Values:</b> `WAU`
# MAGIC 
# MAGIC In <b>Display type</b>, use <b>Bar Chart</b> and click <b>Apply</b>.
# MAGIC 
# MAGIC <img src="https://s3-us-west-2.amazonaws.com/files.training.databricks.com/images/eLearning/Delta/plot-options-bar.png"/>
# MAGIC 
# MAGIC <img alt="Caution" title="Caution" style="vertical-align: text-bottom; position: relative; height:1.3em; top:0.0em" src="https://files.training.databricks.com/static/images/icon-warning.svg"/> order by `week` to seek time-based patterns.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- TODO
# MAGIC 
# MAGIC select week, WAU from mobile_events_delta_gold order by week

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5: Wrap-up
# MAGIC 
# MAGIC * Stop streams

# COMMAND ----------

for s in spark.streams.active:
  s.stop()

# COMMAND ----------

# MAGIC %md
# MAGIC Congratulations: ALL DONE!!

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2020 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>