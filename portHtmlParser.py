#!/usr/bin/env python
# -*- coding: utf-8 -*-
# original version by Enrique Serrano, modified by @jartigag
#
# All code in this project is provided for illustrative and educational purposes only. The code has not been thoroughly tested under all conditions.
# Therefore, no reliability is guaranteed and any damage resulting from using this tool is disclaimed. 
# All code is provided to you "AS IS" without any warranties of any kind.
# You can redistribute it and/or modify it under your responsability.

from bs4 import BeautifulSoup
import urllib2
import csv
from portScanner import Port

def getPortFromHTML(html):
	"""
	This function extracts port info and trims HTML to avoid HTML tags colitions.

	:param html: string with the HTML code of the row containing port info

	:return obj 'Port': returns a new Port object with the info extracted from the HTML
	"""

	# Extract port number and trim HTML
	portNum = extract(html, '<tr><td>', '</td>')
	html = endtrim(html, '</td>')
	# Extract port service and trim HTML
	service = extract(html, '<td>', '</td>')
	html = endtrim(html, '</td>')
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

def endtrim(s, startDelimiter):
	"""
	This function trims a string from the delimiter passed as a parameter to end position

	:param s: string with the HTML code
	:param finalDelimiter: HTML tag or tags indicating how far to trim

	:return obj 'str': returns a trimmed version of param "s"
	"""

	try:
		# Start position
		delimiter = s.index(startDelimiter) + len(startDelimiter)
		# Return trimmed HTML code
		return s[delimiter:]
	except ValueError as e:
		# startDelimiter is not in s
		return s

def starttrim(s, finalDelimiter):
	"""
	This function trims a string from position 0 to the delimiter passed as a parameter

	:param s: string with the HTML code
	:param finalDelimiter: HTML tag or tags indicating where to start to trim

	:return obj 'str': returns a trimmed version of param "s"
	"""

	try:
		# End position
		delimiter = s.index(finalDelimiter) + len(finalDelimiter) - 1
		# Return trimmed HTML code
		return s[:delimiter]
	except ValueError as e:
		# finalDelimiter is not in s
		return s

def parsePorts():
	"""
	This function gets a list of all well-known ports (TCP and UPD)

	:return obj 'allPorts': returns an array. each element is a string with a port and which service or protocol uses it
	"""

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

def dumpPortsInCSV(array,file):
	"""
	This function dumps an array of Ports into a .csv file

	:param array: array with the Port objects
	:param file: target file

	:return true if everything is fine, false if there was any error
	"""

	try:
		with open(file, "wb") as outfile:
			writer = csv.writer(outfile, delimiter=',')
			for port in array:
				writer.writerow([starttrim(port.portNum,"/"),port.service,port.details]) # trimming needed for cases such as "102/tcp"
		return True
	except Exception as e:
		print(e)
		return False
