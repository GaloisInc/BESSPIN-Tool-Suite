# SSITH-FETT-Target smoke tests
Smoke testing is a type of software testing that determines whether 
the deployed build is stable or not. Smoke tests are a minimal set 
of tests run on each build and serves for quickly checking the major 
functions.

## Smoke tests for SQlite database
The SQlite smoke tests provided in ``database.py``file, are developed 
to verify requirements described in ``database_requirements.lando`` document 
and they are part of `FETT` platform testing service.

The following workflow has been implemented:
* create a database instance called `test.db`
``` 
sqlite ~/test.db
```
* create virtual table `food` containing the column `title` and using the `FTS3` search extension
~~~~sqlite
CREATE VIRTUAL TABLE IF NOT EXISTS food USING fts3(title);
~~~~
* insert record into table `food` 

```sqlite
INSERT INTO food(title) VALUES('Pancakes');
```
* verify and update an existing record.

```sqlite
UPDATE food SET title = 'Pizza' WHERE title = 'Pancakes';
```
* verify and delete an existing record.

```sqlite
DELETE FROM food WHERE title = 'Pizza';
```
* drop non existing table.

```sqlite
DROP TABLE IF EXISTS food1;
```
* drop an existing table.

```sqlite
DROP TABLE IF EXISTS food;
```
* drop the database instance `test.db`
```
rm -f ~/test.db
```

  

 
 