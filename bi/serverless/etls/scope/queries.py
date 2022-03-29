class Query():
    def __init__(self, mode='daily'):
        
        self.__NEW_FREEMIUM_CLAIM_QUERY_BASE = """
            SELECT DISTINCT
                RIGHT(json_unquote(json_extract(payload,'$.cellphone')),10) AS cellphone,
                created_at AS first_freemium_arrive_date,
                json_unquote(json_extract(payload,'$.parent_channel')) AS parent_channel,
                json_unquote(json_extract(payload,'$.partnership')) AS partnership
            FROM
                event_logs
            WHERE
                event_type = 'new_freemium_claim'
            AND
                created_at
        """

        self.__OPT_IN_QUERY_BASE = """
            SELECT DISTINCT
                RIGHT(json_unquote(json_extract(payload, '$.cellphone')),10) as cellphone,
                json_unquote(json_extract(payload, '$.template_id')) as template_id,
                created_at as opt_in_date
            FROM
                event_logs
            WHERE
                event_type = 'opt_in'
            AND
                created_at
        """

        self.__FREEMIUM_QUERY_BASE = """
            SELECT DISTINCT
                c.cellphone, o.purchased_at, i.sku, p.title
            FROM
                cuatro_uno.store_orders o
                    JOIN
                cuatro_uno.store_order_items i ON o.id = i.order_id
                    JOIN
                cuatro_uno.store_customers c on o.customer_id = c.id
                    LEFT JOIN
                cuatro_uno.hired_services hs on hs.order_id = o.id
                    LEFT JOIN
                cuatro_uno.products p on hs.product_id = p.id
            WHERE
                i.sku IN ('FREEMIUM0521ACCIDENTES',
                    'DR247FREEMIUM',
                    'FREEMIUM0521ESPECIALISTA',
                    'FREEMIUM0521VIDA',
                    'FREEMIUM0921ATNPSICOLOGICA',
                    'FREEMIUM0921HOGAR',
                    'FREEMIUM0921CHECKUP',
                    'FREEMIUM0921DENTAL')
                    AND o.state IN ('FULFILLED' , 'WAITING_PAYMENT')
            AND
                o.purchased_at
        """
        
        if mode == "daily":
            self.__query_end = ' > %(yesterday)s'
        elif mode == "historical":
            self.__query_end = ' <= %(yesterday)s'
        
        self.NEW_FREEMIUM_CLAIM_QUERY = self.__NEW_FREEMIUM_CLAIM_QUERY_BASE + self.__query_end
        
        self.OPT_IN_QUERY = self.__OPT_IN_QUERY_BASE + self.__query_end
        
        self.FREEMIUM_QUERY = self.__FREEMIUM_QUERY_BASE + self.__query_end