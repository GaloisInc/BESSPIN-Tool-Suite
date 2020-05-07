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
~~~bash 
sqlite ~/test.db
~~~
* create virtual table `food` containing the column `title` and using the `FTS3` search extension
~~~~sql
CREATE VIRTUAL TABLE IF NOT EXISTS food USING fts3(title);
~~~~
* insert record into table `food` 

~~~~sql
INSERT INTO food(title) VALUES('Pancakes');
~~~~
* verify and update an existing record.

~~~~sql
UPDATE food SET title = 'Pizza' WHERE title = 'Pancakes';
~~~~
* verify and delete an existing record.

~~~~sql
DELETE FROM food WHERE title = 'Pizza';
~~~~
* drop non existing table.

~~~~sql
DROP TABLE IF EXISTS food1;
~~~~
* drop an existing table.

~~~~sql
DROP TABLE IF EXISTS food;
~~~~
* and finally drop the database instance `test.db`
~~~bash 
rm -f ~/test.db
~~~

## Smoke tests for  nginx server






  

 
 