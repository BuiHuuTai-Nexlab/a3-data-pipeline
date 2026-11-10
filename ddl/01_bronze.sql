CREATE SCHEMA IF NOT EXISTS `a3-retail-dwh-project.bronze_layer`;

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.bronze_layer.merchant` (
  merchant_id STRING,
  phone_e164 STRING,
  phone_carrier STRING,
  merchant_name STRING,
  street_address STRING,
  ward_name STRING,
  district_name STRING,
  province_code STRING,
  province_name STRING,
  region_name STRING,
  category_l1_name STRING,
  category_l2_name STRING,
  source_systems STRING,
  source_record_count INT64,
  dq_status STRING,
  dq_issues STRING,
  ingested_at TIMESTAMP,
  bronze_ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.bronze_layer.ward` (
  ward_code INT64,
  ward_name STRING,
  ward_full_name STRING,
  ward_name_no_accent STRING,
  ward_type STRING,
  province_code INT64,
  latitude FLOAT64,
  longitude FLOAT64,
  bronze_ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.bronze_layer.province` (
  province_code INT64,
  province_name STRING,
  province_full_name STRING,
  province_name_no_accent STRING,
  province_type STRING,
  region_name STRING,
  latitude FLOAT64,
  longitude FLOAT64,
  bronze_ingested_at TIMESTAMP
);
