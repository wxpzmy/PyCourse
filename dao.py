"""DAO object class for sqlite3 DB
"""
import logging
import sys
import sqlite3
import os

logger = logging.getLogger(__name__)

class DAO:
    """The DAO object for each table to manipulate the resource
    """
    tbname = None

    def __init__(self, tbname, conn):
 
        DAO.tbname = tbname
        self.__conn = conn
        self.__cursor = conn.cursor()
        self.createTable()

    def createTable(self):
        """create table method
        """
        logger.info('DAO: Creating table if not exists {}  ...'.format(DAO.tbname))
        try:
            self.__cursor.execute("""
                create table if not exists {} (id integer primary key autoincrement, url text, name text, data blob)
                """.format(DAO.tbname))
        except sqlite3.Error, e:
            logger.error('Error when create table {}'.format(DAO.tbname), exc_info = True)
            sys.exit(1)  

    def dropTable(self):
        """ Drop current table
        """
        logger.info('DAO: Drop the table {}'.format(DAO.tbname))
        try:
            self.__cursor.execute('drop table if exists {}'.format(DAO.tbname))
        except sqlite3.Error, e:
            logger.error('Error when drop table {}'.format(DAO.tbname), exc_info=True)
            sys.exit(1)
    
    # precondition: the row with rc_id exists
    def addResources(self, rc_id,  rc_data):
        """ Insert resource into the table
        """
        logger.info('DAO: Adding resource for id {}'.format(rc_id))
        try:
            # Handle Binary Case
            rc_data_binary = sqlite3.Binary(rc_data)  
            self.__cursor.execute("""
                update {} set data = ? where id = ?
                """.format(DAO.tbname), (rc_data_binary, rc_id))           
            self.__conn.commit()
            logger.info("Successfully add resource for id {}".format(rc_id))
        except sqlite3.Error, e:
            logger.error('Error when adding resource for id {}'.format(rc_id), exc_info=True)
            if self.__conn:
                self.__conn.rollback()
            sys.exit(1)

    def dumpResource(self, dump_directory):
        """ Dump resource into target place in file system
        """
        ret = None
        logger.info("DAO: fetching resources ... ")
        try:
            ret = self.__cursor.execute('select name, data from {} where data is not null'.format(DAO.tbname))
        except sqlite3.Error, e:
            logger.error("Error when dumping resource for {}".format(dump_directory), exc_info=True)
            sys.exit(1)
        
        logger.info("DAO: dumping resources ... ")

        target_loc = dump_directory + '/' + DAO.tbname

        if not os.path.exists(target_loc):
            os.mkdir(target_loc)
  
        for name, data in ret:
            with open(target_loc + '/' + name, "wb") as f:
                f.write(data)

    def addURLs(self, url_names, urls):
        """ Add URLS into the database if non-exists
        """
        
        logger.info("DAO: Loading URLS into database ... ")
        for name, url in zip(url_names, urls):
            try:
                # check whether the url already in DB
                ret = self.__cursor.execute("""
                      select exists(select * from {} where name = ?)
                      """.format(DAO.tbname), (name,)).fetchone()[0]
                if not ret:
                    self.__cursor.execute("""
                      insert into {} (url, name, data) values (?, ?, ?)
                      """.format(DAO.tbname), (url, name, None))
                    self.__conn.commit()

            except sqlite3.Error, e:
                logger.error("Error when adding urls.", exc_info=True)
                if self.__conn:
                    self.__conn.rollback()
                sys.exit(1)  


    def fetchEmpty(self, iter_num):
        """ Fetch entry with empty data in a given range
        """
        ret = None
        try:
            ret = self.__cursor.execute("""
            select id, url from (select * from {} where data is ? limit ?)
            """.format(DAO.tbname), (None, iter_num)).fetchall()
        except sqlite3.Error, e:
            logger.error("Error when fetch empty.", exc_info=True)
            sys.exit(1)
        logger.debug(ret)
        ids = [elem[0] for elem in ret]
        logger.debug(ids)
        urls = [elem[1] for elem in ret]
        logger.debug(urls)
        return ids, urls


