# BESSPIN Applications #

This directory should includes the instructions and source codes for the bug bounty applications.

In this document, we provide a brief description of each application chosen, the rationale behind choosing it, and the reason behind the tool's choice and the version.

## Table Of Contents ##

- [FreeRTOS](#freertos)
  - [HTTP](#http)
  - [OTA](#ota)
- [UNIX](#unix)
  - [Webserver](#webserver)
  - [Database](#database)
  - [SSH Server](#ssh-server)
  - [Other](#other-unix-applications)

## FreeRTOS ##

To include the known vulnerabilities in FreeRTOS, we choose to use [FreeRTOS v.10.0.1](https://github.com/FreeRTOS/FreeRTOS/releases/tag/V10.0.1). More details about the CVEs related to this version can be found in [the vulnerabilities coverage document](./vulnerabilitiesCoverage.md).

### HTTP ###

The hypertext transfer protocol is the primary protocol used to send data between a web browser and a website. Historically, HTTP requests to servers exposed a lot of vulnerabilities in its stack. Choosing HTTP as the first application to demonstrate the contribution of a SSITH processor to a server security is a *no-brainer*.


### OTA ###

Over the air (OTA) updates allows an IoT manufacturers to update the firmware of the devices already deployed/purchased. This is crucial for security as any vulnerabilities in the product need to be patched to protect the consumers. Living in the beginning of the IoT era, we choose to demonstrate how a SSITH hardware can protect the OTA stack running on top of an IoT device. Especially given that billions of IoT devices use such a comparable network design, but do not have a cryptographer involved in the protocol design.

Amazon FreeRTOS describes [their standard](ttps://www.freertos.org/ota/index.html) in performing OTA using AWS and devices registration. However, we choose to implement a lighter OTA protocol/sequence aiming to simplify the researcher's objective, and let them focus on what SSITH really cares about: the SSITH hardware. Towards this end, we choose to implement the OTA using a simple TFTP server/client connections with signed payloads for authenticity. 

The pre-requisites for this application are a TFTP server/client connections, signature verification (we choose to use Ed25519 using [WolfSSL](https://www.wolfssl.com/) v.3.6.0), and a FAT filesystem where an update payload will be stored.

## UNIX ##

We decide to use the generic term `UNIX` for both Linux Debian and FreeBSD.

### Webserver ###

The rationale behind choosing a webserver is the same as for the FreeRTOS HTTP. We choose to use `nginx` version 1.13.12 with the following modules:

- All modules enabled by default
- `ngx_http_ssl_module`
- `ngx_http_v2_module`

This choice is explained below.

- **Debian:**

Debian website lists the available web servers [here](https://wiki.debian.org/WebServers). This is a compiled list of most of
  the ones which are supported (or might be built) on RV64, light enough for our application, and with relatively recent versions:
  - [Apache (httpd)](https://httpd.apache.org/)
  - [Cherokee](https://cherokee-project.com/) (not tested on low frequencies)
  - [dhttpd](https://github.com/kevmoo/dhttpd)
  - [lighttpd](https://www.lighttpd.net/)
  - [mini-httpd](https://acme.com/software/mini_httpd/)
  - [Nginx](https://www.nginx.com/)
  - [Yaws](http://yaws.hyber.org/)


- **FreeBSD:**

This is a compiled list of some of the available web servers that might be built on RV64:
  - [Apache (httpd)](https://httpd.apache.org/)
  - [Nginx](https://www.nginx.com/)
  - [lighttpd](https://www.lighttpd.net/)

Given our low-frequency operation, and that Nginx uses the least CPU according to many online comparisons, and has more support and more recent vulnerabilities than lighttpd. **Nginx** will be used as our FETT web server. We choose v.1.13.12 to make sure the web server contains known vulnerabilities.


### Database ###

Most server applications use a database. In particular, in the past two decades, the explosion in amounts of data opened the world's eye to how important is storing, accessing, manipulating, and protecting data. Databases represent now more than just record keeping tools. Our entire lives are stored in some of those storage clouds. This also means that every database tool was closely inspected and many software vulnerabilities were found in these databases. We choose to demonstrate SSITH hardware capabilities in protecting **SQLite** version 3.22.0. This choice is explained below.

For the sake of FETT, no need for all-featured full-blown databases like [OracleDB](https://www.oracle.com/database/) (not FreeBSD compatible), [MySQL](https://www.mysql.com/), [PostgresSQL](https://www.postgresql.org/), [MariaDB](https://mariadb.org/), etc.  

Since no-SQL is the current hype, and because all developers are thinking *big data*, we have a limited selection of not-quite-lightweight open-source relational databases like [SQLite](https://github.com/sqlite/sqlite), [Apache Derby](https://github.com/apache/derby), [FireBird](https://github.com/FirebirdSQL/firebird), [Drizzle](https://github.com/stewartsmith/drizzle), [LiteDB](https://github.com/mbdavid/LiteDB), [SQLectron](https://github.com/sqlectron/sqlectron-term), [LucidDB](https://github.com/LucidDB/luciddb), and [H2](https://www.h2database.com/html/main.html).

FireBird and Drizzle are in C++, LiteDB is in C\#, while all of Apache Derby, SQLectron, LucidDB, and H2 are in Java/Javascript. Surprisingly, this basically leaves us with only one option: SQLite. Therefore, **SQLite** will be used as our FETT database. We choose v.3.22.0 to make sure the database contains known vulnerabilities.


### SSH Server ###

[OpenSSH](https://www.openssh.com/) is a standard SSH server with well known vulnerabilities in recent versions, which makes it a good fit for FETT. We will use version 7.3 as it contains several vulnerabilities and is somewhat recent. 

Given how SSITH is tightly related to operating systems, giving the researcher an unpriviledged shell prompt access seems natural.

SSH server pre-requisites include an OpenSSL library, which is also needed by nginx.

### Other UNIX Applications ###

In addition to the aforementioned applications, we provide some additional initial suggestions:

- **TFTP server:** The File Transfer Protocol (FTP) is a well known mechanism, and supported/provided by every modern operating system. Protecting files transfer and server downloads seem like an attractive option as it is both simple and commonly used.

  Since the HTTPS webserver already offers an example of using a protected transport layer, using a simple TFTP (Trivial FTP) server that is over unprotected UDP exposes a different part of the operating system and the network stack. 

  Being a very simple protocol, there is not one implementation or a famous tool that is specialized in TFTP, it is just a feature included in programs handling more than one protocol. One of the open source options that are C-based is [uftpd](https://github.com/troglobit/uftpd). It does not have many vulnerabilities as it is very simple, but allows the researcher to interact with the target through UDP and receiving files from the target's filesystem. If we elect to offer a tftp option, we would choose version v.2.10 as it precedes the patching of the main two vulnerabilities cited [here](https://www.cybersecurity-help.cz/vdb/SB2020010612). 

- **Mail server:** Managing the security and the privacy of a mail server is not trivial, and this is one of the main reasons most businesses end up paying third-parties mail service providers to host their business email domains. Demonstrating SSITH hardware capabilities on a mail server would be interesting to anyone who have previously dealt with email security concerns.

  For FETT purposes, we would prefer a lightweight service, but mail servers are usually heavy like [sendmail](https://doxfer.webmin.com/Webmin/Sendmail_Mail_Server) and [iRedMail](https://www.iredmail.org/). Here's a list of some of the open source C-based mail servers: [postfix](https://github.com/vdukhovni/postfix/tree/master/postfix), [cyrus-imapd](https://github.com/cyrusimap/cyrus-imapd), [exim](https://github.com/Exim/exim), [qmail](https://github.com/amery/qmail), and [citadel](http://citadel.org/doku.php). There is no need to design a [complete system](https://www.debian.org/releases/etch/sparc/ch08s05.html.en) with an MUA (mail user agent), MTA (mail transfer agent), and an MDA (mail delivery agent). Cyrus is mainly for IMAP (as an MDA), Postfix and Qmail are well maintainted and do not have many vulnerabilities, so they would shadow what SSITH has to offer. Exim seems a good choice for our purposes. 

  We choose [Exim v.4.82.1](https://github.com/Exim/exim/releases/tag/exim-4_82_1) as a simple MTA with enough vulnerabilities to manifest SSITH's hardware capabilities. 
  
### Debian System Utilities ###

In addition to default system utilities and services, we install the the following extra packages: 

  - netcat 
  - keyutils
  - pciutils
  - openssh-server
  - usbutils
  - rng-tools
  
  
Here is the list of active services running in Debian:

  - init.scope                                 
  - session-c5.scope                                    
  - dbus.service                              
  - nginx.service                   
  - rng-tools.service
  - rsyslog.service                                    
  - serial-getty@ttySIF0.service                               
  - ssh.service                                 
  - systemd-journald.service                                       
  - systemd-logind.service                                            
  - systemd-udevd.service                      
  - user@0.service                               
  - dbus.socket                             
  - syslog.socket                                              
  - systemd-journald-dev-log.socket                                    
  - systemd-journald.socket                                       
  - systemd-udevd-control.socket                                     
  - systemd-udevd-kernel.socket
  

We disable and mask certain Debian system utilities that are not required to boot to a shell:

  - systemctl disable cron.service
  - systemctl disable dbus-org.freedesktop.timesync1.service
  - systemctl disable e2scrub_reap.service
  - systemctl disable networking.service
  - systemctl disable systemd-timesyncd.service
  - systemctl disable remote-fs.target
  - systemctl disable apt-daily-upgrade.timer
  - systemctl disable apt-daily.timer
  - systemctl disable e2scrub_all.timer
  - systemctl disable logrotate.timer
  - systemctl mask network-online.target
  - systemctl mask sys-fs-fuse-connections.mount
  - systemctl mask apt-daily-upgrade.service
  - systemctl mask apt-daily.service
  - systemctl mask container-getty@.service
  - systemctl mask dbus-org.freedesktop.hostname1.service
  - systemctl mask dbus-org.freedesktop.locale1.service
  - systemctl mask dbus-org.freedesktop.login1.service
  - systemctl mask dbus-org.freedesktop.timedate1.service
  - systemctl mask e2scrub@.service
  - systemctl mask e2scrub_all.service
  - systemctl mask e2scrub_fail@.service
  - systemctl mask fstrim.service
  - systemctl mask getty-static.service
  - systemctl mask kmod.service
  - systemctl mask logrotate.service
  - systemctl mask module-init-tools.service
  - systemctl mask systemd-bless-boot.service
  - systemctl mask systemd-fsck-root.service
  - systemctl mask systemd-fsck@.service
  - systemctl mask systemd-fsckd.service
  - systemctl mask systemd-journal-flush.service
  - systemctl mask systemd-modules-load.service
  - systemctl mask systemd-update-utmp-runlevel.service
  - systemctl mask systemd-update-utmp.service
  - systemctl mask systemd-fsckd.socket
  - systemctl mask bluetooth.target
  - systemctl mask time-sync.target
  - systemctl mask systemd-tmpfiles-clean.timer
  - systemctl mask sys-subsystem-net-devices-eth0.device

