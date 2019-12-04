""" Import data to PostgreSQL database """

import getpass

import sqlalchemy
import sqlalchemy.engine.reflection
import sqlalchemy.engine.url
import sqlalchemy_utils
from pyhelpers.ops import confirmed


class RailwayCodesPSQL:
    def __init__(self, username='postgres', password=None, host='localhost', port=5432, database_name='postgres'):
        """
        We need to be connected to the database server in order to execute the "CREATE DATABASE" command. There is a 
        database called "postgres" created by the "initdb" command when the data storage area is initialised. If we 
        need to create the first of our own database, we can set up a connection to "postgres" in the first instance.
        """
        self.database_info = {'drivername': 'postgresql+psycopg2',
                              'username': username,
                              'password': password if password else getpass.getpass('PostgreSQL password: '),
                              'host': host,  # default: localhost
                              'port': port,  # 5432 (default by installation)
                              'database': database_name}

        # The typical form of a database URL is: url = backend+driver://username:password@host:port/database_name
        self.url = sqlalchemy.engine.url.URL(**self.database_info)
        self.dialect = self.url.get_dialect()
        self.backend = self.url.get_backend_name()
        self.driver = self.url.get_driver_name()
        self.user, self.host = self.url.username, self.url.host
        self.port = self.url.port
        self.database_name = self.database_info['database']

        # Create a SQLAlchemy connectable
        self.engine = sqlalchemy.create_engine(self.url, isolation_level='AUTOCOMMIT')
        self.connection = self.engine.connect()

    # Establish a connection to the specified database (named e.g. 'osm_extracts')
    def connect_db(self, database_name='Railway_Codes'):
        """
        :param database_name: [str] (default: 'Railway_Codes') name of a database
        """
        self.database_name = database_name
        self.database_info['database'] = self.database_name
        self.url = sqlalchemy.engine.url.URL(**self.database_info)
        if not sqlalchemy_utils.database_exists(self.url):
            sqlalchemy_utils.create_database(self.url)
        self.engine = sqlalchemy.create_engine(self.url, isolation_level='AUTOCOMMIT')
        self.connection = self.engine.connect()

    # Check if a database exists
    def db_exists(self, database_name):
        result = self.engine.execute("SELECT EXISTS("
                                     "SELECT datname FROM pg_catalog.pg_database "
                                     "WHERE datname='{}');".format(database_name))
        return result.fetchone()[0]

    # An alternative to sqlalchemy_utils.create_database()
    def create_db(self, database_name='Railway Codes and other data'):
        """
        :param database_name: [str, 'Railway Codes and other data'(default)] name of a database

        from psycopg2 import OperationalError
        try:
            self.engine.execute('CREATE DATABASE "{}"'.format(database_name))
        except OperationalError:
            self.engine.execute(
                'SELECT *, pg_terminate_backend(pid) FROM pg_stat_activity WHERE username=\'postgres\';')
            self.engine.execute('CREATE DATABASE "{}"'.format(database_name))
        """
        if not self.db_exists(database_name):
            self.disconnect()
            self.engine.execute('CREATE DATABASE "{}";'.format(database_name))
            self.connect_db(database_name=database_name)
        else:
            print("The database already exists.")

    # Get size of a database
    def get_db_size(self, database_name=None):
        """
        :param database_name: [str; None (default)] name of database
        :return:
        """
        db_name = '\'{}\''.format(database_name) if database_name else 'current_database()'
        db_size = self.engine.execute('SELECT pg_size_pretty(pg_database_size({})) AS size;'.format(db_name))
        print(db_size.fetchone()[0])

    # Kill the connection to the specified database
    def disconnect(self, database_name=None):
        """
        :param database_name: [str; None(default)] name of database to disconnect from

        Alternative way:
        SELECT
            pg_terminate_backend(pg_stat_activity.pid)
        FROM
            pg_stat_activity
        WHERE
            pg_stat_activity.datname = database_name AND pid <> pg_backend_pid();
        """
        db_name = self.database_name if database_name is None else database_name
        self.connect_db('postgres')
        self.engine.execute('REVOKE CONNECT ON DATABASE {} FROM PUBLIC, postgres;'.format(db_name))
        self.engine.execute(
            'SELECT pg_terminate_backend(pid) '
            'FROM pg_stat_activity '
            'WHERE datname = \'{}\' AND pid <> pg_backend_pid();'.format(db_name))

    # Kill connections to all other databases
    def disconnect_all_others(self):
        self.connect_db('postgres')
        self.engine.execute('SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid();')

    # Drop the specified database
    def drop(self, database_name=None):
        """
        :param database_name: [str; None (default)] database to be disconnected; None: to disconnect the current one
        """
        db_name = self.database_name if database_name is None else database_name
        if confirmed("Confirmed to drop the database \"{}\"?".format(db_name)):
            self.disconnect(db_name)
            self.engine.execute('DROP DATABASE IF EXISTS "{}"'.format(db_name))

    # Create a new schema in the database being currently connected
    def create_schema(self, schema_name):
        """
        :param schema_name: [str] name of a schema
        """
        self.engine.execute('CREATE SCHEMA IF NOT EXISTS "{}";'.format(schema_name))

    # Drop a schema in the database being currently connected
    def drop_schema(self, *schema_names):
        """
        :param schema_names: [str] name of one schema, or names of multiple schemas
        """
        if schema_names:
            schemas = tuple(schema_name for schema_name in schema_names)
        else:
            schemas = tuple(
                x for x in sqlalchemy.engine.reflection.Inspector.from_engine(self.engine).get_schema_names()
                if x != 'public' and x != 'information_schema')
        if confirmed("Confirmed to drop the schema(s): {}".format(schemas)):
            self.engine.execute(('DROP SCHEMA IF EXISTS ' + '%s, '*(len(schemas) - 1) + '%s CASCADE;') % schemas)

    # Check if a table exists
    def table_exists(self, schema_name, table_name):
        """
        :param schema_name: [str] name of a schema
        :param table_name: [str] name of a table
        :return: [bool]
        """
        result = self.engine.execute("SELECT EXISTS("
                                     "SELECT * FROM information_schema.tables "
                                     "WHERE table_schema='{}' "
                                     "AND table_name='{}');".format(schema_name, table_name))
        return result.fetchone()[0]

    # Import data (as a pandas.DataFrame) into the database being currently connected
    def dump_data(self, data, schema_name, table_name, if_exists='replace', chunk_size=None):
        """
        :param data: [pandas.DataFrame]
        :param schema_name: [str]
        :param table_name: [str] name of the targeted table
        :param if_exists: [str] 'fail', 'replace', or 'append'; default 'replace'
        :param chunk_size: [int; None]
        """
        if schema_name not in sqlalchemy.engine.reflection.Inspector.from_engine(self.engine).get_schema_names():
            self.create_schema(schema_name)

        if not data.empty:
            data.coordinates = data.coordinates.map(lambda x: x.wkt)
            data.other_tags = data.other_tags.astype(str)
        data.to_sql(table_name, self.engine, schema=schema_name, if_exists=if_exists, index=False, chunksize=chunk_size)

    # Remove tables from the database being currently connected
    def drop_data(self, schema_name, *table_names):
        """
        :param schema_name: [str]
        :param table_names: [str]
        """
        tables = tuple(('{}.\"{}\"'.format(schema_name, table_name) for table_name in table_names))
        self.engine.execute(('DROP TABLE IF EXISTS ' + '%s, '*(len(tables) - 1) + '%s CASCADE;') % tables)
