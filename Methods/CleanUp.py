from sqlalchemy import create_engine
import urllib
import pyodbc
from datetime import datetime
# Logger
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='output'+ datetime.now().strftime('%Y%m%d%H%M%S')+'.log', level=logging.DEBUG, datefmt='%m/%d %I:%M:%S %p')
# create logger
logger = logging.getLogger('simple_example3')
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
        
#############################################   
# Methods Used in Single Association Rules
#############################################

# Clean Up Single Rules (df 'rules' does NOT contain multiple items)
def cleanUpResultsSingle(rules):
    try:
        rules['antecedents'],rules['consequents']=rules['antecedents'].apply(lambda x: ''.join(map(str, x))),rules['consequents'].apply(lambda x: ''.join(map(str, x)))
        rules['type'], rules['antecedents'], rules['consequents'] = rules['antecedents'].apply(lambda x: x[:1] ), rules['antecedents'].apply(lambda x: x[1:]).astype(int), rules['consequents'].apply(lambda x: x[1:]).astype(int)
        rules=rules.drop(['lift','leverage','conviction'], axis=1)
        return rules
    except Exception as e:
        output(e)
        
# Export Single Rules to Sql Tables (Rules)    
def exportToSqlSingle(varDB,varTable,rules):   
    try:
        output("Export Rules to Sql")
        output("[ Time ]",datetime.now().time())
        params = urllib.parse.quote_plus(varDB)                                 
        conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
        engine = create_engine(conn_str)
        rules.to_sql(name=varTable, con=engine, if_exists='replace', index_label='Id', chunksize=100)   
    except Exception as e:
        output(e)
    
#############################################   
# Methods Used in Multiple Association Rules
#############################################

# Create New DF
def createNewDF(rules, columnname):
    try:
        output("Creating: ",columnname)
        rules[columnname+' length'] = rules[[columnname]].apply(lambda x: len(x))
        df=rules[[columnname]].copy()
        df[columnname]=df[columnname].apply(lambda x: ' '.join(map(str, x)))
        df=df.set_index(df.index)[columnname].str.split(' ', expand=True).stack().reset_index(name=columnname).drop('level_1',1).rename(columns={'level_0':'ruleId'})
        df['itemId'], df['type'] = df[columnname].apply(lambda x: x[1:]).astype(int), df[columnname].apply(lambda x: x[:1] )
        return df
    except Exception as e:
        output(e)

# Clean Up
def convertToSingle(rules):
    try:
        rules=rules[~rules.antecedents.str.contains(" ")]
        rules=rules[~rules.consequents.str.contains(" ")]
        return rules
    except Exception as e:
        output(e)
    

# Clean Up
def cleanUpResults(rules):
    try:
        rules=rules.drop(['lift','leverage','conviction'], axis=1)
        return rules
    except Exception as e:
        output(e)
    
# Export Rules to Sql Tables (Rules, Antecedents, Consequents)  
def exportToSql(varDB,varTable,rules,rules_antecedents,rules_consequents):    
    try:
        output("Export Rules to Sql")
        output("[ Time ]",datetime.now().time())
        params = urllib.parse.quote_plus(varDB)                                 
        conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
        engine = create_engine(conn_str)
        rules.iloc[:,2:].to_sql(name=varTable, con=engine, if_exists='replace', index_label='Id', chunksize=100)
        rules_antecedents.to_sql(name=varTable+'_Ant', con=engine, if_exists='replace', index=False, chunksize=100)
        rules_consequents.to_sql(name=varTable+'_Con', con=engine, if_exists='replace', index=False, chunksize=100)
    except Exception as e:
        output(e)