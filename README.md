## pycourse project: one command multi-course

### How to setup:

   * Requires sqlite3 database in your system. 
   * Further database support will be added later. 
   * pip install -r requirements.txt
   * setup yaml configuration file in conf directory.
   * If any confusion, see the site-template.yaml as example
   * Modify logging.yaml if your want.
   * Run with: pycourse
   * --help or -h with further help for argument.
   
### Features:

   All the downloading material will be stored in Sqlite3 DB. And each course has a .db file in db directory. The db format of resources will be much easier for further analysis and extended for more feature. And another good thing is sqlite db file is protable for any platform.
   
   Like Apache Maven's phase property, pycourse is also divied into four phase:
   
   * launch : just download the all the url into db
   * download : fetch the resources based on the url in db
   * dump : dump the resources from db into local file system
   * cleanup: drop the table in db.

   With --action configuration, the whole process can be easily controlled and tuned.

### Basic Design

  * The Driver (pycourse) is written in Python 2.7.
  * The basic working flow in driver:
    * parsing argument 
    * setup log configuration 
    * setup setup site configuration
    * sanity check on configuration
    * perform login operation for session generation
    * launch downloading in multiprocess for each course matrial
  * The basic working flow in downloader:
    * Request the html from the course-website
    * Filter material
    * Use DAO object to interact with db.
    
### Issue:

* More suitable exception handling should be used in this project.
* More proper log information could be used.
* The project is only tested in Ubuntu 12.04LTS.
* The back-end can be extended to more db option.
* The configuration could be more flexiable.
* Cookie and Session handling can be more smooth.
* Will be better if some GUI can be added in this project.
