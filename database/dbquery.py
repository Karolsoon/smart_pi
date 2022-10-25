from database.postgresdriver import pgDriver


class Query():
    def __init__(self, pgdriver: pgDriver, schema: str):
        self._pgd = pgdriver
        self._schema = schema
        self.query = ''

    def execute(self, query):
        with self._pgd as pgdb:
            pgdb.cursor.execute(query)
            return tuple(pgdb.cursor.fetchall())

    def get_schemas(self, excluded: str):
        query = f"""
            SELECT DISTINCT
                schema_name
            FROM 
                information_schema."schemata" s
            WHERE
                lower(catalog_name) = '{self._pgd.DBNAME.lower()}' AND
                lower(schema_name) NOT IN ({excluded});
        """
        return self.execute(query)

    def get_tables(self, table_type: str):
        """
        Returns table names from the drivers current DB and Query schema.
        Table_type options: view, base table, foreign
        """
        query = f"""
            SELECT DISTINCT
                table_name
            FROM 
                information_schema."tables" t
            WHERE 
                lower(table_schema) = '{self._schema.lower()}' AND
                lower(table_type) = '{table_type.lower()}';
        """
        return self.execute(query)

    def get_columns(self, table: str, metadata_columns):
        query = f"""
            SELECT
                {','.join(metadata_columns)}
            FROM
                information_schema."columns" c
            WHERE
                lower(table_name) = '{table.lower()}'
        """
        return self.execute(query)

    def get_latest_home_measures(self):
        query = f"""
            WITH base_query AS (
                SELECT
                    ROW_NUMBER() OVER (PARTITION BY room ORDER BY ts_id desc) AS "latest",
                    *
                FROM 
                    {self._schema}.home_measures hm
                ORDER BY 
                    latest ASC,
                    room ASC
                LIMIT 20
            )

            SELECT 
                ts_id, room, temperature, pressure, humidity
            FROM base_query
            WHERE latest = 1
            ORDER BY 
                latest ASC,
                room ASC
        """
        return self.execute(query)

    def insert_sensor_data(self, table: str, data: dict[dict]):
        """
        Inserts rows into provided table.
        data format-> {row: {column1: value, column2: value, columnN: value}}
        """
        query = f"""
            INSERT INTO {self._schema}.{table} 
            ({','.join(str(k) for k in data[1].keys())}) VALUES 
            """
        for row in data.values():
            query = query + f"({','.join(str(v) for v in row.values())}),"
        with self._pgd as pgdb:
            pgdb.cursor.execute(query[:-1])
            pgdb.connection.commit()
