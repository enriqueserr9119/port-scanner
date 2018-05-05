"""
	File name: portScanner.py
	Author: Enrique Serrano, Javier Artiga
	Date created: 04/15/2018
	Date last modified: 04/15/2018
	Python version: 2.7

	All code in this project is provided for illustrative and educational purposes only. The code has not been thoroughly tested under all conditions.
	Therefore, no reliability is guaranteed and any damage resulting from using this tool is disclaimed. 
	All code is provided to you "AS IS" without any warranties of any kind.
	You can redistribute it and/or modify it under your responsability.
"""

#TODO: apparently some scanPort threads never end. why?

import socket
import urllib2
import os
import re
import sys
import time
import subprocess
from threading import Thread
import csv
import portHtmlParser

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

def scanPort(hostIP, port):
	"""
	This function checks if a specified port is listening.

	:param hostIP: target host IP address
	:param port: Port object

	:return: returns nothing
	"""

	# Create socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5)

	# Check if port is listening
	if s.connect_ex((hostIP, int(port.portNum))) == 0:
		# Get port info
		listeningPorts.append(port)
	s.close()

listeningPorts = []

if __name__ == "__main__":

	# IP address pattern
	pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

	while(True):
		# Ask the user for an IP address
		hostIP = str(raw_input("\n Introduce the host's IP address: "))

		# Check if the user's input is a valid IP address
		if pattern.match(hostIP):
			time.sleep(1.2)
			print("\n Checking host connection...")
			# Check if host is alive (ping)
			p = subprocess.Popen(["ping", "-q", "-c", "3", hostIP], stdout = subprocess.PIPE, stderr=subprocess.PIPE) # discard stdout, stderr
			lostPackets = p.wait()
			if not lostPackets:
				time.sleep(1.2)
				print("\n * SUCCESS: Host is up")
				break
			else:
				print("\n * FAILED: Host is not alive")
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

	time.sleep(1.2)
	print("\n Looking for listening ports...")
	time.sleep(1.2)

	# All well-known ports (1-1024)
	# Get port info from CSV file
	allPorts = []
	with open('ports.csv', "rb") as f:
		reader = csv.reader(f)
		for row in reader:
			port = Port(row[0], row[1], row[2])
			allPorts.append(port)

	# Check which well-known ports are listening
	threads = []
	for port in allPorts:
		thread = Thread(target = scanPort, args = (hostIP, port))
		thread.start()
		threads.append(thread)

	# Concurrency
	for thread in threads:
		thread.join()

	# Show result
	if len(listeningPorts) > 0:
		print("\n\n ***************** LISTENING PORTS ***************** ")
		for port in listeningPorts:
			print("\n  - %s (%s) --> %s" % (port.service, port.portNum, port.details))
		print(" *************************************************** \n")
	else:
		print("\n No listening ports found \n")