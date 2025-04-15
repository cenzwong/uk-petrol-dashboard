from pyspark.sql import functions as F
from pyspark.sql import SparkSession, DataFrame
from datetime import date

def extract(json_path) -> DataFrame:
    # Read JSON file
    return spark.read.json(json_path)

def transformation(df: DataFrame) -> DataFrame:
    return df.select(
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

def load(df: DataFrame) -> None:
    df.to_csv(f'data/shell/shell_fuel_prices_{today_str}.csv', index=False)

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Read Shell Fuel Prices JSON").getOrCreate()

    # Get today's date
    today_str = date.today().isoformat()

    # File path
    json_path = f"data/shell/shell_fuel_prices_{today_str}.json"


    extract(json_path).transform(
        transformation
    ).transform(
        load
    )