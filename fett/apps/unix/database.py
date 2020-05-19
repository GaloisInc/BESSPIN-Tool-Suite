#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *


@decorate.debugWrap
@decorate.timeWrap
def install(target):
    # target is a fett target object
    printAndLog("Installing sqlite...")
    outLog = ''
    # All we need to do is install sqlite into a suitable location,
    # like /usr/bin
    outLog += target.runCommand("echo \"Installing sqlite into /usr/bin...\"")[1]
    outLog += target.runCommand("install sqlite /usr/bin",erroneousContents=["install:"])[1]
    printAndLog("Sqlite installed successfully.")
    return outLog

@decorate.debugWrap
@decorate.timeWrap
def deploy(target):
    printAndLog ("Deployment successful. Target is ready.")
    
    #Here we should send a message to the portal

    #Here we should wait for a termination signal from the portal
    
    printAndLog("Termination signal received. Preparing to exit...")
    return ''

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    return deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    printAndLog("Testing sqlite...")
    outLog = ''
    sqlite_bin = '/usr/bin/sqlite'
    xDb = 'test.db'
    tableName = 'food'
    foodstuff = 'Pancakes'
    target.switchUser()

    def create_database_and_table(xTable=tableName):
        textBack = ''
        printAndLog(f"Test[create_database_and_table]: Create sqlite {xDb} database and {xTable} table", doPrint=False)
        textBack += target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      erroneousContents=["Error:","near","error"], endsWith="sqlite>")[1]
        textBack += target.runCommand(f"CREATE VIRTUAL TABLE IF NOT EXISTS {xTable} USING fts3(title);",
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")[1]
        textBack += target.runCommand(".exit")[1]
        printAndLog(f"Test[create_database_and_table]: The {xDb} database and {xTable} table created successfully!",
                    doPrint=False)
        return textBack

    def insert_record(xTable=tableName, title_val=foodstuff):
        textBack = ''
        printAndLog(f"Test[insert_record]: Insert into  {xTable} table value {title_val}.", doPrint=False)
        textBack += target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")[1]
        textBack += target.runCommand(f"INSERT INTO {xTable}(title) VALUES('{title_val}');",
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(f"SELECT * from {xTable};", expectedContents=[f"{title_val}"], expectExact=True,
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(".exit")[1]
        printAndLog(
            f"Test[insert_record]: The value {title_val} has been successfully inserted into {xTable} table!",
            doPrint=False)
        return textBack

    def update_record(xTable=tableName, title_val=foodstuff):
        textBack = ''
        printAndLog(f"Test[update_record]: Update the first record in the table {xTable}  - value {title_val}.",
                    doPrint=False)
        textBack += target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")[1]
        textBack += target.runCommand(f"SELECT * from {xTable};", expectExact='Pancakes', endsWith="sqlite>")[1]

        textBack += target.runCommand(f"UPDATE {xTable} SET title='{title_val}' WHERE title ='Pancakes';",
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(f"SELECT * from {xTable};", expectExact=True, expectedContents=[f"{title_val}"],
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(".exit")[1]
        printAndLog(f"Test[update_record]: The first record has been successfully updated - value {title_val}.",
                    doPrint=False)
        return textBack

    def delete_record(xTable=tableName, title_val=foodstuff):
        textBack = ''
        printAndLog(f"Test[delete_record]: Delete {title_val} from the {xTable} table.", doPrint=False)
        textBack += target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")[1]
        textBack += target.runCommand(f"SELECT * from {xTable};", expectExact=True, expectedContents=[f"{title_val}"],
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(f"DELETE FROM {xTable} WHERE title='{title_val}';",
                                      endsWith="sqlite>")[1]
        textBack += target.runCommand(f"SELECT * from {xTable};", expectedContents=[], endsWith="sqlite>")[1]
        textBack += target.runCommand(".exit")[1]
        printAndLog(
            f"Test[delete_record]: The value {title_val} has been successfully deleted from the {xTable} table!",
            doPrint=False)
        return textBack

    def drop_table(xTable=tableName):
        textBack = ''
        printAndLog(f"Test[drop_table]: Drop {xTable} table", doPrint=False)
        textBack += target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>")[1]
        retCommand = \
            target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>", shutdownOnError=False,
                              suppressErrors=True)
        textBack += retCommand[1]
        if (not retCommand[0]):
            textBack += target.runCommand(".exit")[1]
            printAndLog(f"Test[drop_table]: Invalid input parameter table {xTable}. Provide valid table name.", doPrint=False)
        else:
            textBack += target.runCommand(f"DROP TABLE IF EXISTS {xTable};", endsWith="sqlite>")[1]
            textBack += target.runCommand(".tables", expectedContents=[], endsWith="sqlite>")[1]
            textBack += target.runCommand(".exit")[1]
            printAndLog(f"Test[drop_table]: The {xTable} table has been dropped successfully!", doPrint=False)
        return textBack

    def drop_database(pathToFile='~'):
        textBack = ''
        printAndLog(f"Test[drop_database]: Drop sqlite {xDb} database", doPrint=False)
        if target.doesFileExist(xFile=xDb, pathToFile=pathToFile, shutdownOnError=False):
            textBack += target.runCommand(f"rm -f {pathToFile}/{xDb}")[1]
            printAndLog(f"Test[drop_database]: Database {xDb} dropped successfully!", doPrint=False)
        else:
            target.shutdownAndExit(f"\nTest[drop_database]: Failed to find <{pathToFile}/{xDb}> on target.", exitCode=EXIT.Run)
        return textBack

    outLog += create_database_and_table()
    outLog += insert_record()
    outLog += update_record(title_val='Pizza')
    outLog += delete_record(title_val='Pizza')
    outLog += drop_table(xTable='food1')
    outLog += drop_table()
    outLog += drop_database()
    printAndLog("Sqlite tests OK!")
    return outLog
