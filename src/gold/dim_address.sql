BEGIN TRANSACTION;

DELETE FROM `a3-retail-dwh-project.gold_layer.dim_address` WHERE TRUE;

INSERT INTO `a3-retail-dwh-project.gold_layer.dim_address` (
  address_sk, street_address, ward_sk, province_sk, valid_from_date, valid_to_date, is_current
)
WITH merchant_address AS (
  SELECT
    address,
    ward_id,
    province_id,
    MIN(valid_from_date) AS valid_from_date,
    IF(LOGICAL_OR(is_current), NULL, MAX(valid_to_date)) AS valid_to_date,
    LOGICAL_OR(is_current) AS is_current
  FROM `a3-retail-dwh-project.silver_layer.merchant`
  GROUP BY address, ward_id, province_id
)
SELECT
  TO_HEX(MD5(TO_JSON_STRING(STRUCT(a.address, a.ward_id, a.province_id)))) AS address_sk,
  a.address AS street_address,
  w.ward_sk,
  p.province_sk,
  a.valid_from_date,
  a.valid_to_date,
  a.is_current
FROM merchant_address AS a
LEFT JOIN `a3-retail-dwh-project.gold_layer.dim_ward` AS w
  ON w.ward_id = a.ward_id AND w.is_current = TRUE
LEFT JOIN `a3-retail-dwh-project.gold_layer.dim_province` AS p
  ON p.province_id = a.province_id AND p.is_current = TRUE;

COMMIT TRANSACTION;
