# SSITH-FETT-Target Nginx smoke tests

This document describes the smoke tests run on deployment for the FETT Nginx
webserver app. The tests are derived from the requirements for the application,
outlined in the Lando specification. 

The tests are fairly simple, as verifying that the required features are enabled
is straightforward.

## Test 0: serving http

The first test merely checks that the web server is running and serving pages by
requesting the index page over HTTP. The server should respond with a 200
status code.

## Test 1: Nginx is compiled with SSL support

The SSL test is to request a page from the server via the HTTPS protocol over
the HTTPS port. The server should respond with a 200 status code.

## Test 2: Nginx is compiled with HTTP2 support

The HTTP2 test is nearly identical to the SSL test, except the request is made
using the HTTP/2 protocol, not HTTP/1.1.

## Test 3: Error redirection

The Nginx server should be configured with error redirection. To that end, we
request a resource that is supposed to be hidden, expecting status code 302
(redirect).

## Test 4: "Hidden" resource

This is a quick sanity check that there is a "hidden" resource. We request the
same resource as in test 3, but specify the server name via the "Host" header.
As this is a target for error page smuggling, we actually do want this resource
to only be protected by obscurity.
