See Python3 code in contact.py.
Development notes are in development.txt

The "contact" program uses Selenium version 2.47.1 and the Firefox driver.
All other libraries should be standard, although urllib.parse may be require a recent Python.

There is a 'hack' in the program that will only work on my systems.  This provides a fixed path for a FirefoxProfile to avoid a Selenium bug.  (none of the solutions found work for me, which mostly involve just updating selenium)
The code is conditional on the platform.system() and  marked 'FIXME'.
