from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from database import insert_detection

def main():
    spark = SparkSession.builder \
        .appName("DustCloudDetection") \
        .getOrCreate()

    # Define the schema for Kafka message
    schema = StructType([
        StructField("timestamp", StringType(), True),
        StructField("camera_id", StringType(), True),
        StructField("frame_id", IntegerType(), True),
        StructField("track_id", IntegerType(), True),
        StructField("bbox", StringType(), True)
    ])

    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "detection_topic") \
        .load()

    # Deserialize JSON message
    df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Process and store the data
    def process_row(row):
        insert_detection(row.timestamp, row.camera_id, row.frame_id, row.track_id, row.bbox)

    query = df.writeStream \
        .foreachBatch(lambda batch_df, _: batch_df.foreach(process_row)) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
