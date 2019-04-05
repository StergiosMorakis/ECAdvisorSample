# Import Libraries
import time
from datetime import datetime
import urllib
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from Methods.QueryReader import *
from Methods.CleanUp import *
from mlxtend.frequent_patterns import apriori, association_rules
sys.path.remove(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from sqlalchemy import create_engine
import urllib
from datetime import datetime
import time
# Logger
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='output'+ datetime.now().strftime('%Y%m%d%H%M%S')+'.log', level=logging.DEBUG, datefmt='%m/%d %I:%M:%S %p')
# create logger
logger = logging.getLogger('simple_example1')
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
    finalLog = ""
    for prnt in s:
        finalLog += " " + str(prnt)
    logger.info(finalLog)
    
# Link Categories
def earlyGameFunc(varDB):
    output("[ Time ]",datetime.now().time(), "=== Early Game ===")
    executeQuery('../Initializers/Update Category_Tree.sql', varDB)
    executeQuery('../Initializers/Update Product_Category_Mapping.sql',varDB)
    executeQuery('../Initializers/Update Product_Category_Mapping_Desc.sql',varDB)
    executeQuery('../Initializers/Update Product_Group_Mapping.sql',varDB)    
    executeQuery('../Initializers/Unique_Group_Combination.sql', varDB)
    executeQuery('../Initializers/Product_Specs_Mapping.sql', varDB)
    executeQuery('../Initializers/Ratings.sql', varDB)

# Produce Rules
def midGameFunc(varQuery, varTable, varDB, varMinSupp=1):
    output("=== Mid Game ===")
    output("[ Time ]",datetime.now().time(), "Source Query:",varQuery,"\nExport to:",varDB,"\non Table:",varTable)
    # Get Dataframe with Cols [DividerId], [ItemId], [Quantity]
    df = getTable(varQuery, varDB)
    ordercount = len(df.DividerId.unique())
    itemcount = len(df.ItemId.unique())
    mean = df.groupby('DividerId')['ItemId'].count().mean()
    if(varMinSupp == 1):
        varMinSupp = (mean/itemcount)

    output('[ => ] Order Count:',ordercount,'\n[ => ] Item Count:',itemcount,'\n[ => ] Avg Items Per Order:',mean,'\n[ => ] Min Support:', varMinSupp)    
    # Encode
    output("Encode")
    basket = (df.groupby(['DividerId', 'ItemId'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('DividerId'))   
    # Turn Quantities from >0 to 1
    def encode_units(x):
        if x <= 0:
            return 0
        if x > 0:
            return 1
    basket_sets = basket.applymap(encode_units)
    # Training Apriori on the dataset
    output("[ Time ]",datetime.now().time(), "Training Apriori on the dataset")
    frequent_itemsets = apriori(basket_sets, min_support=varMinSupp, max_len=2, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.01)   

    output("[ RULES : ]", rules.shape[0])

    # Clean Up Results
    output("Clean Up Results",rules.shape)
    rules['antecedents length'], rules['consequents length'] = rules.antecedents.apply(lambda x: len(x)), rules.consequents.apply(lambda x: len(x))
    rules['antecedents'] = rules['antecedents'].apply(lambda x: ' '.join(map(str, x)))
    rules['consequents'] = rules['consequents'].apply(lambda x: ' '.join(map(str, x)))
    rules = rules[~rules.antecedents.str.contains(" ")]
    rules = rules[~rules.consequents.str.contains(" ")]
    # Ungroup Antecedents using row as index
    rules_antecedents = rules[['antecedents']].copy()
    rules_antecedents['itemId'], rules_antecedents['type'] = rules_antecedents['antecedents'].apply(lambda x: x[1:] ), rules_antecedents['antecedents'].apply(lambda x: x[:1] )
    # Ungroup Consequents using row as index
    rules_consequents = rules[['consequents']].copy()
    rules_consequents['itemId'], rules_consequents['type'] = rules_consequents['consequents'].apply(lambda x: x[1:] ), rules_consequents['consequents'].apply(lambda x: x[:1] )
    rules = rules.drop(['lift', 'leverage', 'conviction'], axis=1)
    # Export Rules to Sql Table
    output("[ Time ]",datetime.now().time() , "Export Rules to Sql Table")
    params = urllib.parse.quote_plus(varDB)
    conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
    engine = create_engine(conn_str)
    rules.iloc[:,2:].to_sql(name=varTable, con=engine, if_exists='replace', index_label='Id', chunksize=100)
    rules_antecedents.to_sql(name=varTable+'_Ant', con=engine, if_exists='replace', index_label='ruleid', chunksize=100)
    rules_consequents.to_sql(name=varTable+'_Con', con=engine, if_exists='replace', index_label='ruleid', chunksize=100)

# Produce Results
def lateGameFunc(varDB):
    output("=== Late Game ===")
    output(datetime.now().time())
    executeQuery('ProduceResults/Update Suggestions.sql', varDB)

# Main Func Initializer
def mainFunc(varName, varTable='Exxxx', varLateGame=True, varMinSupp=1):
    try:
        starttime = time.time()
        output("************************")
        output("[ Start Time ]",datetime.now().time())
        output("************************")
        output("*********  START "+varName+" START  **********")
        varDB = getConnectionString(varName, 1)
        if not checkTablesExist('../Initializers/checkTablesExist.sql', varDB):
            earlyGameFunc(varDB)
        midGameFunc(varQuery='ImportData/DataQuery.sql', varTable=varTable+'_Cl2', varDB=varDB, varMinSupp=varMinSupp)
        if(varLateGame):
            lateGameFunc(varDB)
        output("*********  END "+varName+" END  **********")
        output("************************")
        output("[ End Time ]",datetime.now().time())
        endtime = time.time()
        output("[ Duration ]",(endtime-starttime))
    except Exception as e:
        output(e)

# Runs
mainFunc(varName='dbName', varTable='E0009', varLateGame=True, varMinSupp=0)

