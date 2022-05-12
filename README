Web Serial To eBook
===================

Small script to generate ebook files from web serials like Worm for use on an ebook reader.

Supported Serials
-----------------

 * Worm by J.C. McCrae (https://parahumans.wordpress.com/)
 * Ward by J.C. McCrae (http://www.parahumans.net)
 * Pact by J.C. McCrae (https://pactwebserial.wordpress.com/)

Requirements
------------

 * Docker 19+

Build Container
---------------

    $ docker build -t webserialtoebook:latest .
    
Usage
-----

Show help:

    $ ./webserialtoebook

List supported web serials:

    $ ./webserialtoebook list

List all pages and associated URLs of a serial:

    $ ./webserialtoebook pages worm

Fetch all pages of a serial and store them locally:

    $ ./webserialtoebook fetch worm

Compile previously fetched pages from a serial into an epub file:

    $ ./webserialtoebook compile worm
