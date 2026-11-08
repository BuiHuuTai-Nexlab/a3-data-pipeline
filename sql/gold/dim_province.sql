BEGIN TRANSACTION;

DELETE FROM `a3-retail-dwh-project.gold_layer.dim_province` WHERE TRUE;

INSERT INTO `a3-retail-dwh-project.gold_layer.dim_province` (
  province_sk, province_id, province_name, province_full_name, province_type,
  region_name, latitude, longitude, valid_from_date, valid_to_date, is_current
)
SELECT
  province_sk, province_id, province_name, province_full_name, province_type,
  region_name, latitude, longitude, valid_from_date, valid_to_date, is_current
FROM `a3-retail-dwh-project.silver_layer.province`;

COMMIT TRANSACTION;
