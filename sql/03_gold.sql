CREATE SCHEMA IF NOT EXISTS `a3-retail-dwh-project.gold_layer`;

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.gold_layer.dim_category` (
  category_sk STRING,
  category_l1_code STRING,
  category_l1_name STRING,
  category_l2_code STRING,
  category_l2_name STRING,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.gold_layer.dim_phone` (
  phone_sk STRING,
  phone_number STRING,
  phone_carrier STRING,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.gold_layer.dim_province` (
  province_sk STRING,
  province_code INT64,
  province_name STRING,
  province_full_name STRING,
  province_type STRING,
  region_name STRING,
  latitude FLOAT64,
  longitude FLOAT64,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.gold_layer.dim_ward` (
  ward_sk STRING,
  ward_code INT64,
  ward_name STRING,
  ward_full_name STRING,
  ward_type STRING,
  province_sk STRING,
  latitude FLOAT64,
  longitude FLOAT64,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.gold_layer.dim_address` (
  address_sk STRING,
  street_address STRING,
  ward_sk STRING,
  province_sk STRING,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
);

CREATE TABLE IF NOT EXISTS `a3-retail-dwh-project.gold_layer.dim_merchant` (
  merchant_sk STRING,
  merchant_id STRING,
  merchant_name STRING,
  category_sk STRING,
  phone_sk STRING,
  address_sk STRING,
  valid_from_date DATE,
  valid_to_date DATE,
  is_current BOOL
)
CLUSTER BY is_current, merchant_id;
