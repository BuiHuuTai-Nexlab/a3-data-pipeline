
CREATE SCHEMA IF NOT EXISTS `a3-retail-dwh-project.silver_layer`;

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.silver_layer.province` (
  province_code INT64,
  province_name STRING,
  province_full_name STRING,
  province_type STRING,
  region_name STRING,
  latitude FLOAT64,
  longitude FLOAT64,
  bronze_ingested_at TIMESTAMP,  -- copy từ bronze_loaded_at
  silver_ingested_at TIMESTAMP,  -- lúc job silver này chạy
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.silver_layer.ward` (
  ward_code INT64,
  ward_name STRING,
  ward_full_name STRING,
  ward_type STRING,
  province_code INT64,
  latitude FLOAT64,
  longitude FLOAT64,
  bronze_ingested_at TIMESTAMP,
  silver_ingested_at TIMESTAMP,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.silver_layer.merchant` (
  merchant_id STRING,
  phone STRING,
  phone_carrier STRING,
  merchant_name STRING,
  address STRING,
  ward_code INT64,
  province_code INT64,
  category_l1_name STRING,
  category_l2_name STRING,
  ingested_at TIMESTAMP,         -- từ nguồn (giữ lại từ bronze)
  bronze_ingested_at TIMESTAMP,  -- copy từ bronze_loaded_at
  silver_ingested_at TIMESTAMP,  -- lúc job silver này chạy
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
)
CLUSTER BY is_current, merchant_id;
