BEGIN TRANSACTION;

DELETE FROM `a3-retail-dwh-project.gold_layer.dim_phone` WHERE TRUE;

INSERT INTO `a3-retail-dwh-project.gold_layer.dim_phone` (
  phone_sk,
  phone_number,
  phone_carrier,
  valid_from_date,
  valid_to_date,
  is_current
)
SELECT
  TO_HEX(MD5(TO_JSON_STRING(STRUCT(phone, phone_carrier)))) AS phone_sk,
  phone AS phone_number,
  phone_carrier,
  MIN(valid_from_date) AS valid_from_date,
  IF(LOGICAL_OR(is_current), NULL, MAX(valid_to_date)) AS valid_to_date,
  LOGICAL_OR(is_current) AS is_current
FROM `a3-retail-dwh-project.silver_layer.merchant`
GROUP BY phone, phone_carrier;

COMMIT TRANSACTION;
