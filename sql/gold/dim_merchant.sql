BEGIN TRANSACTION;

DELETE FROM `a3-retail-dwh-project.gold_layer.dim_merchant` WHERE TRUE;

INSERT INTO `a3-retail-dwh-project.gold_layer.dim_merchant` (
  merchant_sk, merchant_id, merchant_name, category_sk, phone_sk, address_sk,
  valid_from_date, valid_to_date, is_current
)
SELECT
  merchant_sk,
  merchant_id,
  merchant_name,
  TO_HEX(MD5(TO_JSON_STRING(STRUCT(category_l1_name, category_l2_name)))) AS category_sk,
  TO_HEX(MD5(TO_JSON_STRING(STRUCT(phone, phone_carrier)))) AS phone_sk,
  TO_HEX(MD5(TO_JSON_STRING(STRUCT(address, ward_id, province_id)))) AS address_sk,
  valid_from_date,
  valid_to_date,
  is_current
FROM `a3-retail-dwh-project.silver_layer.merchant`;

COMMIT TRANSACTION;
