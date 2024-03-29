from database.postgresdriver import pgDriver
from time import sleep


class Query(object):
    def __init__(self, pgdriver: pgDriver, schema: str):
        self._pgd = pgdriver
        self._schema = schema
        self.query = ''

    def execute(self, query):
        try:
            with self._pgd() as pgdb:
                pgdb.cursor.execute(query)
                return tuple(pgdb.cursor.fetchall())
        except AttributeError as err:
            raise ConnectionError('Cannot get cursor') from err

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

    def get_latest(self, table: str) -> list:
        query = f"""
WITH base_query AS (
                SELECT
                    ROW_NUMBER() OVER (PARTITION BY room ORDER BY ts_id desc) AS "latest",
                    *
                FROM 
                    {self._schema}.{table}
                WHERE ts_id >= now() - '10 minutes'::interval
                ORDER BY 
                    latest ASC,
                    room ASC
                LIMIT 200
            )

            SELECT 
                *
            FROM base_query
            WHERE latest = 1
            ORDER BY 
                latest ASC,
                room ASC
        """
        return self.execute(query)

    def insert_sensor_data(self, data: tuple[dict]):
        """
        Inserts rows into provided table.
        data format-> {table: {column1: value, column2: value, columnN: value}}
        """
        for row in data:
            table_name = next(iter(row))
            query = f"""
                INSERT INTO {self._schema}.{table_name}
                ({','.join(str(k).lower() for k in row[table_name].keys())}) VALUES 
                """
            for columns in row.values():
                query = query + f"({','.join(str(v) for v in columns.values())}),"
            with self._pgd() as pgdb:
                pgdb.cursor.execute(query[:-1])
                pgdb.connection.commit()
    
    def get_pressure_trend(self) -> tuple[list]:
        query = f"SELECT pressure_trend, room FROM {self._schema}.pressure_trend"
        try:
            pressure_trend = self.execute(query)
            return pressure_trend[0][0] if pressure_trend[0][0] else 'CONSTANT'
        except IndexError:
            return 'CONSTANT'

    def get_transformed_latest(self, required_tables: tuple[str],
            template: dict[dict]) -> dict:
        """
        Returns a dict with data mapped by rooms. Each room is a separate key,
        values are another dict with column names and values.
        """
        return self._transform_queryset(
            datasets=self._get_data(required_tables),
            template=template
        )

    def _transform_queryset(self, datasets: tuple, template: dict[dict]) -> dict:
        transformed_dataset = {}
        transformed_dataset.update(template)
        for dataset in datasets:
            for row in dataset:
                transformed_dataset[row['room'].lower()].update(
                    {
                        str(k).lower(): str(v)
                        for k, v
                        in row.items()
                        if k not in ['ts_id', 'room', 'insert_ts', 'latest'] \
                        and v is not None
                    }
                )
        return transformed_dataset

    def _get_data(self, required_tables: list[str]) -> tuple[list]:
        return tuple(
                self.get_latest(x)
                for x
                in required_tables
            )
        
