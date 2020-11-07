
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import configparser
from scipy import stats


# Read Config file
config = configparser.ConfigParser()
config.read('config.ini')
conn_str = 'Driver={SQL Server};Server=' + config['SQL_DATABASE']['SERVER'] + ';Database=' + config['SQL_DATABASE'][
    'DATABASE'] + ';Trusted_Connection=yes;'

# DB Connection
conn = pyodbc.connect(conn_str)

# Read Data
queryDF =pd.read_sql_query(config['SQL_QUERY']['QUERY'], conn)
print(queryDF.head())
print(queryDF.info(memory_usage='deep'))
queryDF = queryDF.drop(['order_id','page_id'],axis=1)
print(queryDF.describe(include='all'))
print(queryDF.groupby(['title']).count()['target'])
print(queryDF.groupby('site_version')[['user_id']].count())
print(queryDF.select_dtypes('object').nunique())
# Check missing values
queryDF.isnull().sum()

# product, site_version and title columns have only 5, 2 and 3 unique values, so it is a good opportunity to change them to the category type
for col in ['product', 'site_version', 'title']:
    queryDF[col] = queryDF[col].astype('category')
print(queryDF.info(memory_usage = 'deep'))
queryDF.head()

print('Products on banners: ', queryDF['product'].unique())
print('Site versions: ', queryDF.site_version.unique())
print('Page events: ', queryDF.title.unique())

# Data Analysis

ax=queryDF.groupby(['site_version']).count()['target'].plot.pie(figsize=(7,7),autopct='%1.0f%%')
ax.set_ylabel('')
ax.set_title('Response distributions for different sites')
plt.show()

ax=queryDF.groupby(['title']).count()['target'].plot.pie(figsize=(7,7),autopct='%1.0f%%')
ax.set_ylabel('')
ax.set_title('Response distributions for different titles')
plt.show()

ax=queryDF.groupby(['site_version','title']).count()['target'].unstack('title').plot(kind='bar',figsize=(7,7),grid=True)
ax.set_ylabel('count')
ax.set_title('Breakdowns of titles across different sites')
plt.show()

ax=queryDF.groupby(['product','site_version']).count()['target'].unstack('site_version').iloc[::-1].plot(kind='barh',figsize=(12,15),grid=True)
ax.set_ylabel('product')
ax.set_xlabel('count')
ax.set_title('Overall distributions of product for different sites')
plt.show()



# Statistical Significance
queryDF['intercept']=1
t, p = stats.ttest_ind(
    queryDF.loc[queryDF['site_version'] == 1, 'intercept'].values,
    queryDF.loc[queryDF['site_version'] == 2, 'intercept'].values,
    equal_var=False
)
print("The t-value is %0.10f and the p-value is %0.10f." % (t, p))

