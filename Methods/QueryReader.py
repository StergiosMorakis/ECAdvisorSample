import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import urllib
from datetime import datetime
import re
# Logger
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='output'+ datetime.now().strftime('%Y%m%d%H%M%S')+'.log', level=logging.DEBUG, datefmt='%m/%d %I:%M:%S %p')
# create logger
logger = logging.getLogger('simple_example2')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)   
# create formatter
formatter = logging.Formatter('%(levelname)s - %(message)s')    
# add formatter to ch
ch.setFormatter(formatter)    
# add ch to logger
logger.addHandler(ch)

# Output
def output(*s):
    for prnt in s:
        logger.info(prnt)
    
def getConnectionString(dbname, con_line=0):
    try:
        driver_name = ''
        driver_names = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
        driver_name = driver_names[0]
        conn_str = 'DRIVER={};'.format(driver_name)
        text_file = open("../SQL_connections.txt", "r")
        for cur_line, line in enumerate(text_file):
            if cur_line == con_line:
                conn_str = conn_str + line.replace(re.search('DATABASE=(.+?);', line).group(1), dbname).replace('\n', '')
                break
        text_file.close()
        return conn_str
    except Exception as e:
        output(e)
        raise

# Get Table
def getTable(varQuery,varDB):
    try:
        # Connect to SqlServer
        output(datetime.now().time(), "Import SQL Table to DataFrame using ", varQuery)
        sql_conn = pyodbc.connect(varDB)     
        with open(varQuery, 'r') as targetQuery:
            query=targetQuery.read()
        df = pd.read_sql(query, sql_conn)          
        # Closing database connection
        sql_conn.close()   
        return df
    except Exception as e:
        output(e)
        raise

# Export DataFrame to SQL as Table 
def ExportToSql(varDB, varTable, df):  
    try:
        output(datetime.now().time(), "Export DataFrame to SQL Table named ", varTable)
        params = urllib.parse.quote_plus(varDB)
        conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
        engine = create_engine(conn_str)
        df.to_sql(name=varTable, con=engine, if_exists='replace', chunksize=100)   
    except Exception as e:
        output(e)
        raise

# Execute Query
def executeQuery(varQuery, varDB, dbname=''):
    try: 
        # Connect to SqlServer
        output(datetime.now().time(), "Execute Query ", varQuery)
        sql_conn = pyodbc.connect(varDB)     
        with open(varQuery, 'r') as targetQuery:
            query=targetQuery.read()
        query=query.replace('[DATABASE_NAME].', dbname) 
        cur = sql_conn.cursor()
        cur.execute(query)
        sql_conn.commit()
        # Closing database connection
        sql_conn.close()
    except Exception as e:
        output(e)
        raise

# Check if Tables Exist
def checkTablesExist(varQuery, varDB):
    try:
        output(datetime.now().time(), "Check if Tables exist, Source: ", varQuery)
        sql_conn = pyodbc.connect(varDB)
        cur = sql_conn.cursor()
        with open(varQuery, 'r') as targetQuery:
            query=targetQuery.read()   
        cur.execute(query)
        tables = query.count(',')+1
        # Return True if count of existing Tables == tables
        if cur.fetchone()[0] == tables:
            output('Tables Exist')
            cur.close()
            return True
        else:
            output('Tables Do Not Exist')
            cur.close()
            return False
    except Exception as e:
        output(e)
        raise
