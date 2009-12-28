#!/usr/bin/env python
'''
File			:	zipcode.py
Package			:	usps_webtools.address_verify
Brief			:	Implements the zip code lookup request/response model.
Author			:	William M. Clifford
--------------------------------------------------------------------------------
'''

import os
import xml.dom.minidom

USPS_USER_ID = os.environ['USPS_USER_ID']

# Import the base request and response objects.
from usps_webtools.base import RequestBase, ResponseBase

# Import the USPSAddress class for use with the response/request classes.
from usps_webtools.address_verify.usaddress import USPSAddress

# Grab the utility functions
from usps_webtools.utility import createXmlElement, getXmlElement, getXmlElementContents

#-------------------------------------------------------------------------------
# class: ZipCodeLookupResponse
#-------------------------------------------------------------------------------
class ZipCodeLookupResponse(ResponseBase):
	
	def __init__(self, xmlElement):
		ResponseBase.__init__(self)
		self.__addresses = []
		self._parseElement(xmlElement)
		return
	
	def __str__(self):
		s = ('=' * 72) + '\nUSPS Zip Code Lookup - Response\n' + ('=' * 72) + '\n'
		for k, v in self.__addresses:
			s += 'ADDRESS ID "%s"\n' % k
			s += str(v)
			pass
		return s
	
	@property
	def addresses(self):
		return tuple(self.__addresses)
	
	def _parseElement(self, elem):
		# elem is the XPATH context for the root element
		try:
			root_element = getXmlElement(elem, '/ZipCodeLookupResponse')
		except Exception:
			sys.stderr.write('ZipCodeLookupResponse._parseElement(): XML document root element is not of expected value.\n')
			sys.stderr.write('\tExpecting "<ZipCodeLookupResponse>", got "<%s>".\n' % elem.name)
			return
		# Get each of the addresses that were validated.
		for addr_elem in elem.xpathEval('/ZipCodeLookupResponse/Address'):
			addr_id = addr_elem.prop('ID')
			usps_addr = USPSAddress()
			usps_addr.parseFromXML(addr_elem)
			self.__addresses.append( (addr_id, usps_addr) )
			pass
		return
	
	pass


#-------------------------------------------------------------------------------
# class: ZipCodeLookupRequest
#-------------------------------------------------------------------------------
class ZipCodeLookupRequest(RequestBase):
	SERVER_REQUEST_URI = 'http://production.shippingapis.com/ShippingAPI.dll'
	RESPONSE_CLASS = ZipCodeLookupResponse
	
	def __init__(self):
		RequestBase.__init__(self)
		self._api = 'ZipCodeLookup'
		self.__addresses = {}
		return
	
	def addAddress(self, addr_id, usps_addr):
		if len(self.__addresses) >= 5:
			raise ValueError('USPS zip code lookup only allows up to 5 addresses per request.')
		self.__addresses[addr_id] = usps_addr
		return
	
	def clearAddresses(self):
		self.__addresses.clear()
	
	def _constructDOM(self):
		'''
		Constructs the XML DOM document that describes the contents of the
		Request instance.
		'''
		xd = xml.dom.minidom.Document()
		root_elem = xd.createElement('ZipCodeLookupRequest')
		root_elem.setAttribute('USERID', USPS_USER_ID)
		# We want to add all our addresses.
		addr_ids = self.__addresses.keys()
		addr_ids.sort()
		for addr_id in addr_ids:
			usps_addr = self.__addresses[addr_id]
			usps_addr.appendToXml(addr_id, root_elem)
			pass
		# Don't forget to append the root element, and we're all set.
		xd.appendChild(root_elem)
		return xd
	
	pass

