#!/usr/bin/env python3

import cgi
form = cgi.FieldStorage()
url = form.getfirst("url")
email = form.getfirst("email")

f = open("./test.txt", "x")