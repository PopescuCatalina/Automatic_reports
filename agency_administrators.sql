SELECT ab.agency_id AS 'Agency ID',
		 ug.id AS 'Group ID',
		 a.name AS 'Agency name',
		 ug.name AS 'Couriers group',
       ab.delegate_name AS 'Admin name',
       em.agency_billing_emails AS 'Admin email'
FROM agency_billing_config_entity ab , agency_billing_config_emails em , xdelivery.del_users_groups ug , xdelivery.del2_courier_agency a
WHERE ab.agency_id = em.agency_billing_config_entity_agency_id
AND ab.agency_id = ug.courier_agency_id
AND ab.agency_id = a.id
AND a.deleted = 0
AND ug.deleted = 0
AND a.name NOT LIKE 'Filiale Inactive'