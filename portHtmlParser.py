from bs4 import BeautifulSoup
import urllib2

class Port:
	"""
	This class defines a port info.
	"""
	def __init__(self, portNum, service, details):
		"""
		:param portNum: port number
		:param service: port service
		:param details: port service details
		"""
		self.portNum = portNum
		self.service = service
		self.details = details

def getPortFromHTML(html):
	"""
	This function extracts port info and trims HTML to avoid HTML tags colitions.

	:param html: string with the HTML code of the row containing port info

	:return obj 'Port': returns a new Port object with the info extracted from the HTML
	"""

	# Extract port number and trim HTML
	portNum = extract(html, '<tr><td>', '</td>')
	html = trim(html, '</td>')
	# Extract port service and trim HTML
	service = extract(html, '<td>', '</td>')
	html = trim(html, '</td>')
	# Extract port service details
	details = extract(html, '<td>', '</td></tr>', ommitSpaces=False)

	# Return a new port with the obtained info
	return Port(portNum, service, details)

def extract(s, startDelimiter, finalDelimiter, ommitSpaces=True):
	"""
	This function extracts info between HTML tags.

	:param s: string with the HTML code
	:param startDelimiter: HTML tag or tags indicating where the valid info starts
	:param finalDelimiter: HTML tag or tags indicating where the valid info ends
	:param ommitSpaces (optional, default=True): indicates if spaces should be removed or not

	:return obj 'str': returns a trimmed version of param "s"
	"""

	# Start and end positions
	start = s.index(startDelimiter) + len(startDelimiter)
	end = s.index(finalDelimiter)
	# Return valid info
	if ommitSpaces:
		return s[start:end].strip(' \n\t')
	else:
		return s[start:end].strip('\n\t')

def trim(s, finalDelimiter):
	"""
	This function trims a string from position 0 to the delimiter passed as a parameter

	:param s: string with the HTML code
	:param finalDelimiter: HTML tag or tags indicating how far to trim

	:return obj 'str': returns a trimmed version of param "s"
	"""

	# End position
	delimiter = s.index(finalDelimiter) + len(finalDelimiter)
	# Return trimmed HTML code
	return s[delimiter:]

def parsePorts():

	allPorts = []

	# Get HTML
	html = urllib2.urlopen('http://web.mit.edu/rhel-doc/4/RH-DOCS/rhel-sg-en-4/ch-ports.html').read()
	soup = BeautifulSoup(html, 'html.parser')

	# Parse HTML to find ports info
	tableRows = soup.find('table', class_='CALSTABLE').find('tbody').findChildren('tr')
	for row in tableRows:
		allPorts.append(getPortFromHTML(str(row)))

	# Return filled array
	return allPorts