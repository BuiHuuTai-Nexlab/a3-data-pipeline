BEGIN TRANSACTION;

DELETE FROM `a3-retail-dwh-project.gold_layer.dim_ward` WHERE TRUE;

INSERT INTO `a3-retail-dwh-project.gold_layer.dim_ward` (
  ward_sk,
  ward_id,
  ward_name,
  ward_full_name,
  ward_type,
  province_sk,
  latitude,
  longitude,
  valid_from_date,
  valid_to_date,
  is_current
)
SELECT
  w.ward_sk,
  w.ward_id,
  w.ward_name,
  w.ward_full_name,
  w.ward_type,
  p.province_sk,
  w.latitude,
  w.longitude,
  w.valid_from_date,
  w.valid_to_date,
  w.is_current
FROM `a3-retail-dwh-project.silver_layer.ward` AS w
LEFT JOIN `a3-retail-dwh-project.gold_layer.dim_province` AS p
  ON p.province_id = w.province_id AND p.is_current = TRUE;

COMMIT TRANSACTION;
