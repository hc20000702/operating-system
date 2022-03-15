import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SqlalchemyDatabaseUrl="mysql+pymysql://root:chenhx103572@127.0.0.1:3306/manage"
# SqlalchemyDatabaseUrl="mysql+pymysql://root:13874431908@hc@127.0.0.1:3306/manage"
SqlalchemyDatabaseUrl="mysql+pymysql://erp:ERPplus2022@gz-cynosdbmysql-grp-izok5e41.sql.tencentcdb.com:27939/erp"
engine = create_engine(SqlalchemyDatabaseUrl)
SessionLocal=sessionmaker(autocommit=False,bind=engine)
Base=declarative_base()