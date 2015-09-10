#!/usr/bin/env python
#
from selenium import webdriver
from urllib.parse import urlparse,urlunparse
import urllib.request

import logging
import pdb
import re
import sys
import platform

class ui:
    """ web access with ui capabilities """
    def __init__(self,hack=''):
        """ Selenium web driver can be set up 'headless' browser on some remote system, which could improve performance or allow running multiple copies"""
        if hack:
            self.web = webdriver.Firefox(webdriver.FirefoxProfile(hack))
        else:
            self.web = webdriver.Firefox()

        self.actions = webdriver.common.action_chains.ActionChains(self.web)
        #self.scan.actions.getCurrentWindow().focus()
        for _ in range(12):
            self.actions.send_keys(webdriver.common.keys.Keys.TAB)
        #for _ in range(3)
        #    self.actions.send_keys(webdriver.common.keys.Keys.PAGE_DOWN)

        # perform actions later
    def __enter__(self):
        return self
    def __exit__(self,t,v,s):
        self.web.quit()

scheduled = set() # deque? avoid duplicate scheduling
done = set() # web pages already examined
emails = set() # email addresses found

def normalized(link):
    url = urlparse(link)
    urlparts = list(url)
    if urlparts[0] == 'http' or urlparts[0] == '':
        urlparts[0] = 'http'
    urlparts[0] = str.lower(urlparts[0]) # scheme
    urlparts[1] = str.lower(urlparts[1]) # netloc
    if 'mailto' == urlparts[0]:
        urlparts[2] = str.lower(urlparts[2]) # email address in path
    urlparts[3] = '' # parms
    urlparts[4] = '' # query
    urlparts[5] = '' # fragment
    return urlunparse(urlparts)

def test_domain(domain,desired):
    return bool(not(desired) or re.search('[\.]'+desired+'$',domain))

class Links:
    """ iterator for links on a web page """
    def __str__(self):
        return str({'domain': self.domain,'page':self.page,'scheduled':self.found,'emails':self.mail})

    def __init__(self,scan,page,domain):
        self.scan = scan 
        self.page = page
        self.domain = domain
        self.mail = set()
        try:
            #scan.web.manage().timeouts().implicitlyWait(10,TimeUnit.SECONDS)
            self.scan.web.get(page)
            # TODO: deal with model dialogs
            # TODO: check if page really html?
            # TODO: set focus on page first, before any key commands
            scan.actions.perform()
            #pdb.set_trace()
            aa = '//a[@href]'
            aas = self.scan.web.find_elements_by_xpath(aa)
            href = [normalized(a.get_attribute('href')) for a in aas]
            # links with domain
            lsd = set([h for h in href if test_domain(urlparse(h).netloc,self.domain)])
            # relative links (or mailto)
            rls = set([h for h in href if 'http' not in h])
            self.mail = set([h[7:] for h in href if 'mailto' in h])
            self.found = lsd|rls
        except: # limit catches to HTTP or parsing exceptions?
            self.found = set() # bad links or selenium exceptions on stale elements ?

    def __iter__(self):
        return self

    def __next__(self):
        
         while (0 < len(self.found)):
             link = self.found.pop() # str = type(link)
             url = urlparse(normalized(link))
             scheme = str(url.scheme)
             if 0 == len(scheme) or (re.match('http',scheme) and test_domain(str(url.netloc),self.domain)):
                 todo = urlunparse(url)
                 return todo
         raise StopIteration

def headers(page):
    ret = {'Content-Type':None,'ETag':None}
    try:
        with urllib.request.urlopen(page) as response:
             ret = response.info()
    except:
        pass # ignore any errors, in particular 404
    return ret

logging.basicConfig()
log = logging.getLogger('fe')

def is_html(content_type):
    if content_type:
        for mime in ['text/html','application/xhtml+xml']:
            if mime in content_type:
                return True
    return False

def isdigit(c):
    return c in '0123456789'

if __name__ == '__main__':

    # FIXME: see readme.md
    hack = ''
    if 'Linux' == platform.system():
        hack = '/home/pi/.mozilla/firefox/m9f853mx.default'

    domain = '<domain>'
    usage = sys.argv[0] + ' [-v(erbose)|-d(ebug)] ' + domain
    if 1 < len(sys.argv):
        if '-t' == sys.argv[1]:
            log.setLevel(logging.DEBUG)
            #pdb.set_trace()
            assert(test_domain('blog.jana.com','jana.com'))
            assert(not(test_domain('foo.com','foo.company.net')))
            contacts = Links(ui(hack),'http://jana.com/contact','jana.com')
            log.debug(str(contacts))
            for email in contacts.mail:
                print(email)
            contacts.scan.web.close()
            exit(0)
        elif '-v' == sys.argv[1]:
            log.setLevel(logging.INFO)
            domain = sys.argv[2]
        elif '-d' == sys.argv[1]:
            log.setLevel(logging.DEBUG)
            domain = sys.argv[2]
            pdb.set_trace()
        else:
            domain = sys.argv[1]
    else:
        print(usage)
        exit(1)

    with ui(hack) as scan:
        """
        #pdb.set_trace()
        """
        page = normalized('http://www.'+domain)
        scheduled.add(page)
        while(scheduled):
            page = scheduled.pop()
            if page not in done:
                done.add(page)
                log.info('page={}'.format(page))
                header = headers(page)
                etag = header['ETag']
                if is_html(header['Content-Type']) and etag not in done:
                        if etag:
                            done.add(header['ETag'])
    
                        links = Links(scan,page,domain)
                        for email in links.mail:
                            emails.add(email)
                            print(email)

                        log.debug('links found={}'.format(links.found))
                        diff = links.found  - done
                        log.debug('diff={}'.format(diff))
                        scheduled |= diff
                        log.debug('done={}'.format(done))

        #log.info('scheduled={}'.format(scheduled))
        #log.info('done={}'.format(done))
        log.info('{} emails={} found in {} pages of {}'.format(len(emails),emails,len([p for p in done if not(isdigit(p[0]))]),domain))
        """
        # pdb.set_trace()
        try:
            for l in ls:
                log.info(l)
        except:
            log.error('{} is not iterable'.format(ls))
        """
