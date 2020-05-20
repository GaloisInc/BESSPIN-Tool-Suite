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

    # All we need to do is install sqlite into a suitable location,
    # like /usr/bin
    target.runCommand("echo \"Installing sqlite into /usr/bin...\"",tee=getSetting('appLog'))
    target.runCommand("install sqlite /usr/bin",erroneousContents=["install:"],tee=getSetting('appLog'))
    printAndLog("Sqlite installed successfully.")
    return

@decorate.debugWrap
@decorate.timeWrap
def deploy(target):
    printAndLog ("Deployment successful. Target is ready.")
    
    #Here we should send a message to the portal

    #Here we should wait for a termination signal from the portal
    
    printAndLog("Termination signal received. Preparing to exit...")
    return

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    printAndLog("Testing sqlite...")
    sqlite_bin = '/usr/bin/sqlite'
    xDb = 'test.db'
    tableName = 'food'
    foodstuff = 'Pancakes'
    target.switchUser()
    appLog = getSetting('appLog')

    def create_database_and_table(xTable=tableName):
        printAndLog(f"Test[create_database_and_table]: Create sqlite {xDb} database and {xTable} table", doPrint=False)
        target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      erroneousContents=["Error:","near","error"], endsWith="sqlite>",tee=appLog)
        target.runCommand(f"CREATE VIRTUAL TABLE IF NOT EXISTS {xTable} USING fts3(title);",
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>",tee=appLog)
        target.runCommand(".exit",tee=appLog)
        printAndLog(f"Test[create_database_and_table]: The {xDb} database and {xTable} table created successfully!",
                    doPrint=False)
        return

    def insert_record(xTable=tableName, title_val=foodstuff):
        printAndLog(f"Test[insert_record]: Insert into  {xTable} table value {title_val}.", doPrint=False)
        target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>",tee=appLog)
        target.runCommand(f"INSERT INTO {xTable}(title) VALUES('{title_val}');",
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(f"SELECT * from {xTable};", expectedContents=[f"{title_val}"], expectExact=True,
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(".exit",tee=appLog)
        printAndLog(
            f"Test[insert_record]: The value {title_val} has been successfully inserted into {xTable} table!",
            doPrint=False)
        return

    def update_record(xTable=tableName, title_val=foodstuff):
        printAndLog(f"Test[update_record]: Update the first record in the table {xTable}  - value {title_val}.",
                    doPrint=False)
        target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>",tee=appLog)
        target.runCommand(f"SELECT * from {xTable};", expectExact='Pancakes', endsWith="sqlite>",tee=appLog)

        target.runCommand(f"UPDATE {xTable} SET title='{title_val}' WHERE title ='Pancakes';",
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(f"SELECT * from {xTable};", expectExact=True, expectedContents=[f"{title_val}"],
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(".exit",tee=appLog)
        printAndLog(f"Test[update_record]: The first record has been successfully updated - value {title_val}.",
                    doPrint=False)
        return

    def delete_record(xTable=tableName, title_val=foodstuff):
        printAndLog(f"Test[delete_record]: Delete {title_val} from the {xTable} table.", doPrint=False)
        target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>",tee=appLog)
        target.runCommand(f"SELECT * from {xTable};", expectExact=True, expectedContents=[f"{title_val}"],
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(f"DELETE FROM {xTable} WHERE title='{title_val}';",
                                      endsWith="sqlite>",tee=appLog)
        target.runCommand(f"SELECT * from {xTable};", expectedContents=[], endsWith="sqlite>",tee=appLog)
        target.runCommand(".exit",tee=appLog)
        printAndLog(
            f"Test[delete_record]: The value {title_val} has been successfully deleted from the {xTable} table!",
            doPrint=False)
        return

    def drop_table(xTable=tableName):
        printAndLog(f"Test[drop_table]: Drop {xTable} table", doPrint=False)
        target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                      endsWith="sqlite>",tee=appLog)
        retCommand = \
            target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>", shutdownOnError=False,
                              suppressErrors=True,tee=appLog)
        if (not retCommand[0]):
            target.runCommand(".exit",tee=appLog)
            printAndLog(f"Test[drop_table]: Invalid input parameter table {xTable}. Provide valid table name.", doPrint=False)
        else:
            target.runCommand(f"DROP TABLE IF EXISTS {xTable};", endsWith="sqlite>",tee=appLog)
            target.runCommand(".tables", expectedContents=[], endsWith="sqlite>",tee=appLog)
            target.runCommand(".exit",tee=appLog)
            printAndLog(f"Test[drop_table]: The {xTable} table has been dropped successfully!", doPrint=False)
        return

    def drop_database(pathToFile='~'):
        printAndLog(f"Test[drop_database]: Drop sqlite {xDb} database", doPrint=False)
        if target.doesFileExist(xFile=xDb, pathToFile=pathToFile, shutdownOnError=False):
            target.runCommand(f"rm -f {pathToFile}/{xDb}",tee=appLog)
            printAndLog(f"Test[drop_database]: Database {xDb} dropped successfully!", doPrint=False)
        else:
            target.shutdownAndExit(f"\nTest[drop_database]: Failed to find <{pathToFile}/{xDb}> on target.", exitCode=EXIT.Run)
        return

    create_database_and_table()
    insert_record()
    update_record(title_val='Pizza')
    delete_record(title_val='Pizza')
    drop_table(xTable='food1')
    drop_table()
    drop_database()
    printAndLog("Sqlite tests OK!")
    return
