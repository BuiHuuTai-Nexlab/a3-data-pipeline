BEGIN TRANSACTION;

DELETE FROM `a3-retail-dwh-project.gold_layer.dim_category` WHERE TRUE;

-- Nguon chi co ten category, chua co ma nen category_l1_code / category_l2_code de NULL.
INSERT INTO `a3-retail-dwh-project.gold_layer.dim_category` (
  category_sk, category_l1_code, category_l1_name, category_l2_code, category_l2_name,
  valid_from_date, valid_to_date, is_current
)
SELECT
  TO_HEX(MD5(TO_JSON_STRING(STRUCT(category_l1_name, category_l2_name)))) AS category_sk,
  NULL AS category_l1_code,
  category_l1_name,
  NULL AS category_l2_code,
  category_l2_name,
  MIN(valid_from_date) AS valid_from_date,
  IF(LOGICAL_OR(is_current), NULL, MAX(valid_to_date)) AS valid_to_date,
  LOGICAL_OR(is_current) AS is_current
FROM `a3-retail-dwh-project.silver_layer.merchant`
GROUP BY category_l1_name, category_l2_name;

COMMIT TRANSACTION;
