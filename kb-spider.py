import scrapy
import re
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import requests
import json

#before executing the program
#change folder number - numerical corresponding to freshdesk category
#choose the category (source category) eg. scrapy-cloud, portia
#enter the api_key of freshdesk
#to execute - python kb-spider.py

folder = '22000131044'
category = "billing" 
api_key = "<ENTER YOUR API KEY>"

urls = []
articles = []
dict = {}
prefix = 'http://help.scrapinghub.com'

#spider to enumerate the article links
class KBSpider1(scrapy.Spider):
    name = 'kbspider1'
    start_urls = ['http://help.scrapinghub.com/'+category]

    def parse(self, response):
      	    next_page = response.css('a ::attr(href)').extract()
	    for s in next_page:
 	   	 if re.search('^/'+category,s):
			urls.append(prefix+s)

#spider to crawl each article
class KBSpider2(scrapy.Spider):
    name = 'kbspider2'

    def start_requests(self):
          for url in urls:
              yield scrapy.Request(url, self.parse)
	    
    def parse(self, response):
	for block in response.css('div.content'):
		article = block.css('article').extract()
		title = block.css('h2.t__h1 ::text').extract_first()
		if title:
			dict[title] = article

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(KBSpider1)
    yield runner.crawl(KBSpider2)
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished    

#REST API to freshdesk
def createArticle(title,description,keywords):

	domain = "scrapinghub"
	password = "x"
	type = 1
	status = 2
	headers = { 'Content-Type' : 'application/json' }
	solution = {
	    'title' : title,
	    'description' : description[0],
	    'type' : type,
	    'status' : status,
	}

	r = requests.post("https://"+ domain +".freshdesk.com/api/v2/solutions/folders/"+folder+"/articles", auth = (api_key, password), headers = headers, data = json.dumps(solution))

	if r.status_code == 201:
	  print "created successfully, the response is given below" + r.content
	  print "Location Header : " + r.headers['Location']
	else:
	  print "Failed to create, errors are displayed below,"
	  response = json.loads(r.content)
	  print response["errors"]

	  print "x-request-id : " + r.headers['x-request-id']
	  print "Status Code : " + str(r.status_code)


#copy articles to freshdesk
for key in dict:
	createArticle(key, dict[key],'blah')
