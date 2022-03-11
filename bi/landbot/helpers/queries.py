
class Query():
    def __init__(self):
        self.users_companies_match_query = """
            SELECT DISTINCT
                eu.uuid AS 'UUID de beneficiario',
                eu.id AS 'Id de usuario de beneficiario',
                eu.name AS 'Nombre de beneficiario',
                eu.lastname AS 'Apellido paterno de beneficiario',
                eu.second_lastname AS 'Apellido materno de beneficiario',
                bu.uuid AS 'UUID de empleador',
                bu.id AS 'Id de usuario de empleador',
                bu.name AS 'Nombre de empleador',
                bu.lastname AS 'Apellido paterno de empleador',
                bu.second_lastname AS 'Apellido materno de empleador',
                ch.name AS Canal,
                c.name AS Empresa,
                usm.service_user_id
            FROM
                (SELECT
                    system_user_id,
                    service_user_id
                FROM
                    user_service_mappings
                WHERE
                    service_code = 'ZENDESK') usm
                    LEFT JOIN
                users eu ON eu.id = usm.system_user_id
                    LEFT JOIN
                employee_profiles ep ON ep.user_id = eu.id
                    LEFT JOIN
                hired_services hs ON hs.employee_profile_id = ep.id
                    LEFT JOIN
                boss_profiles bp ON bp.id = hs.boss_profile_id
                    LEFT JOIN
                users bu ON bu.id = bp.user_id
                    LEFT JOIN
                store_orders o ON o.id = hs.order_id
                    LEFT JOIN
                c4uno_channels ch ON ch.id = hs.channel_id
                    LEFT JOIN
                companies c ON c.user_id = bu.id
            WHERE
                o.state IN ('FULFILLED', 'WAITING_PAYMENT')
                    AND
                hs.state = 'ACTIVE'
                    AND
                usm.service_user_id IN %(zendesk_ids)s
        """