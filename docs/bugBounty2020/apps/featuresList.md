# Applications Features #
This is an overview of the applications features specified informally in lando documents 
and verified by the smoke tests.

## FreeRTOS ##
These are the features covered by the FreeRTOS application stack, informally described in [LANDO design](../design), and tested in [freertos tests](../../../besspin/fett/freertos/freertos.py).

### HTTP ###

- Hosts a homepage that displays text, image, and a link.
- The homepage links to a version page.

### OTA ###

- OTA listens for clients using TFTP protocol.
- Ed25519  signature verification of a given file, using a known public key, derived 
from a known pass-phrase.
- Updates the version html page hosted by the HTTP server.


## Unix ##
These are the applications features covered by Linux Debian and FreeBSD application stack.

### Web Server (Nginx v.1.13.12) ###
The FETT Nginx web server features are derived from the requirements for the application,
outlined in the [nginx_requirements.lando](../design/nginx_requirements.lando) document 
and covered by the corresponding [smoke tests](../../../besspin/fett/unix/webserver.py).

The following features are tested and verified:
- The ability to check that the web server is running and serving pages by
requesting the index page over HTTP.
- Nginx is compiled with SSL support.
- Nginx is compiled with HTTP2 support providing an ability to make a request 
by using the HTTP/2 protocol.
- The Nginx server is configured with error redirection mechanism.
- Nginx is configured to run a separate 'server' (in its config file) that
protects a named resource.
- The https webpage should be static.
- The page opens another internet webpage through a link.
- The page opens a text file.
- The page opens an image.
- The page receives a request and saves on the local filesystem.
- The page links to another static page.


### Database (SQLite v.3.22.0) ###
The database features are described in [database_requirements.lando](../design/database_requirements.lando) document 
and verified by the [smoke tests](../../../besspin/fett/unix/database.py).

The following features are tested and verified:
- The SQLite is compiled with `FET3` search extension support.
- User permission, privileges and access to execute the sqlite binary. 
- Ability to `CREATE` and `DROP` database files and tables as well as 
to access the ``VIRTUAL`` tables and manipulate resources other than bits in the database file.
- Ability to execute ``DML`` commands including the most common SQL statements such as
`SELECT`, `INSERT`, `UPDATE` and `DELETE`.


