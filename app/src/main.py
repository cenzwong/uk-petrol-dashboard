from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from datetime import date

spark = SparkSession.builder.appName("Read Shell Fuel Prices JSON").getOrCreate()

# Get today's date
today_str = date.today().isoformat()

# File path
json_path = f"data/shell/shell_fuel_prices_{today_str}.json"

# Read JSON file
df = spark.read.json(json_path)



df_unpacked = df.select(
    "last_updated",
    F.explode("stations").alias("stations")
).select(
    F.col("last_updated"),
    F.col("stations")["site_id"].alias("site_id"),
    F.col("stations")["brand"].alias("brand"),
    F.col("stations")["address"].alias("address"),
    F.col("stations")["postcode"].alias("postcode"),
    F.col("stations")["location"]["latitude"].alias("lat"),
    F.col("stations")["location"]["longitude"].alias("lon"),
    F.col("stations")["prices"]["B7"].alias("B7"),
    F.col("stations")["prices"]["E10"].alias("E10")
)

df_unpacked_df = df_unpacked.toPandas()
