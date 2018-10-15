import sqlite3

databaseFilename = ""

def Init(database):
    global databaseFilename
    databaseFilename = database
    createTableIfNotExist()

def createTableIfNotExist():
    conn = sqlite3.connect(databaseFilename)
    cursor = conn.cursor()

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS [debts] ('
        '[Id] integer PRIMARY KEY NOT NULL, '
        '[who] string, '
        '[toWhom] string, '
        '[debt] string);')

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS [history] ('
        '[Id] integer PRIMARY KEY NOT NULL, '
        '[name] string, '
        '[date] datetime, '
        '[message] string);')

    conn.commit()
    conn.close()


def writeToDatabase(who, toWhom, value):
    """
    проверяем, есть ли такая пара людей
    если пары нет, то создаём её
    если пара есть, то плюсуем значение
    """
    result = runQuery("SELECT * FROM debts WHERE who='{0}' AND toWhom='{1}'".format(who, toWhom))
    if len(result) == 0:
        runQuery("INSERT INTO debts (who, toWhom, debt) VALUES ('{0}', '{1}', '{2}')".format(who, toWhom, value))
    else:
        newValue = int(result[0][3]) + int(value)
        runQuery("UPDATE debts SET debt = '{0}' WHERE Id={1}".format(newValue, result[0][0]))
    maintainBase()


def writeHistory(name, date, message):
    runQuery("INSERT INTO history (name, date, message) VALUES ('{0}', '{1}', '{2}')".format(name, date, message))


def getHistory():
    result = runQuery("SELECT * FROM history ORDER BY Id DESC LIMIT 50")    
    return result


def getDebts():
    maintainBase()
    result = runQuery("SELECT * FROM debts")
    return result


def maintainBase():
    base = runQuery("SELECT * FROM debts")
    for i in range(len(base)):
        if base[i][3] == 0:
            runQuery("DELETE FROM debts WHERE id='{0}'".format(base[i][0]))


def runQuery(query):
    conn = sqlite3.connect(databaseFilename)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result
