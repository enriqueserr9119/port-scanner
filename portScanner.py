"""
	File name: portScanner.py
	Author: Enrique Serrano
	Date created: 04/15/2018
	Date last modified: 04/15/2018
	Python version: 2.7

	All code in this project is provided for illustrative and educational purposes only. The code has not been thoroughly tested under all conditions.
	Therefore, no reliability is guaranteed and any damage resulting from using this tool is disclaimed. 
	All code is provided to you "AS IS" without any warranties of any kind.
	You can redistribute it and/or modify it under your responsability.
"""

import socket
import urllib2
import os
import re
import sys
import time
from threading import Thread
from bs4 import BeautifulSoup

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


def binarySearch(targetPortNum, start, end):
	"""
	This function implements a binary search algorithm to find a port in the sorted "allPorts" list.

	:param targetPortNum: port number to find
	:param start: list position to start the search
	:param end: list position to finish the search

	:return obj 'Port': returns the port object matching the given target port number.
						Returns None in case the target port number is not found.
	"""

	# Get mid position port number
	mid = start + (end-start)/2
	num = int(allPorts[mid].portNum)
	# Try to find the port number in the list
	if end-start == 0:
		if num == targetPortNum:
			return allPorts[mid]
		else:
			return None
	elif end-start > 0:
		if num == targetPortNum:
			return allPorts[mid]
		elif num < targetPortNum:
			# Look for the port number in the right.
			return binarySearch(targetPortNum, mid + 1, end)
		elif num > targetPortNum:
			# Look for the port number in the left.
			return binarySearch(targetPortNum, start, mid - 1)


def scanPort(hostIP, portNum):
	"""
	This function checks if a specified port is listening.

	:param hostIP: target host IP address
	:param portNum: port number

	:return: returns nothing
	"""

	# Create socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Check if port is listening
	if s.connect_ex((hostIP, portNum)) == 0:
		# Get port info
		port = binarySearch(portNum, 0, len(allPorts))
		if port != None:
			print("  - %s (%s) --> %s\n" % (port.service, port.portNum, port.details))
		s.close()


# All well-known ports (1-1024)
allPorts = []
# IP address pattern
pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

while(True):
	# Ask the user for an IP address
	hostIP = str(raw_input("\n Introduce the host's IP address: "))

	# Check if the user's input is a valid IP address
	if pattern.match(hostIP):
		time.sleep(1.2)
		print("\n Checking host connection...\n")
		time.sleep(2)
		# Check if host is alive (ping)
		pingCheck = os.system('ping -c 3 ' + hostIP)
		if pingCheck == 0:
			time.sleep(1.2)
			print("\n\n SUCCESS: Host is up")
			break
		else:
			print("\n ** Host is not alive")
			sys.exit("\n Execution stopped\n")
	else:
		print("\n\t** ERROR: not valid IP address")
		again = str(raw_input("\n Try again? (y/n): "))
		if again == "y" or again == "Y":
			continue
		elif again == "n" or again == "N":
			sys.exit("\n Execution stopped\n")
		else:
			sys.exit("\n\t** ERROR: not valid option %s\n" % again)


print("\n\n *************** LISTENING PORTS *************** \n")

# Get HTML
html = urllib2.urlopen('http://web.mit.edu/rhel-doc/4/RH-DOCS/rhel-sg-en-4/ch-ports.html').read()
soup = BeautifulSoup(html, 'html.parser')

# Parse HTML to find ports info
tableRows = soup.find('table', class_='CALSTABLE').find('tbody').findChildren('tr')
for row in tableRows:
	allPorts.append(getPortFromHTML(str(row)))

# Check which well-known ports are listening
for portNum in range(1,1025):
	thread = Thread(target = scanPort, args = (hostIP, portNum,))
	thread.start()
