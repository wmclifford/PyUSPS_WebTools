#!/usr/bin/env python
'''
File			:	addrstandards.py
Package			:	usps_webtools.address_verify
Brief			:	Implements the address standardization request/response model.
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
# class: AddressVerResponse
# inherits: usps_webtools.ResponseBase
#
# Public properties:
#	addresses - tuple; contains zero or more tuples of the form
#		(address id, address), parsed from the XML response sent by the server.
#		The address ID is the ID that was assigned to the address when adding
#		it to the request object. The address is an instance of the USPSAddress
#		class defined above.
#
#-------------------------------------------------------------------------------
class AddressVerResponse(ResponseBase):
	
	def __init__(self, xmlElement):
		ResponseBase.__init__(self)
		self.__addresses = []
		self._parseElement(xmlElement)
		return
	
	def __str__(self):
		s = ('=' * 72) + '\nUSPS Address Verification - Response\n' + ('=' * 72) + '\n'
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
			root_element = getXmlElement(elem, '/AddressValidateResponse')
		except Exception:
			sys.stderr.write('AddressVerResponse._parseElement(): XML document root element is not of expected value.\n')
			sys.stderr.write('\tExpecting "<AddressValidateResponse>", got "<%s>".\n' % elem.name)
			return
		# Get each of the addresses that were validated.
		for addr_elem in elem.xpathEval('/AddressValidateResponse/Address'):
			addr_id = addr_elem.prop('ID')
			usps_addr = USPSAddress()
			usps_addr.parseFromXML(addr_elem)
			self.__addresses.append( (addr_id, usps_addr) )
			pass
		return
	
	pass

#-------------------------------------------------------------------------------
# class: AddressVerRequest
# inherits: usps_webtools.RequestBase
#
# Public methods:
#	addAddress(addr_id, usps_addr)
#		Adds an address to the request that will be sent to the server. The ID
#		is required, as the user may request multiple addresses be verified in
#		a single request. The server limits the number of addresses being
#		verified to a maximum of 5 per request. If there are already 5 addresses
#		in the current request, a ValueError will be raised.
#
#	clearAddresses()
#		Removes all the addresses previously added to the request.
#
#-------------------------------------------------------------------------------
class AddressVerRequest(RequestBase):
	SERVER_REQUEST_URI = 'https://production.shippingapis.com/ShippingAPI.dll'
	RESPONSE_CLASS = AddressVerResponse
	
	def __init__(self):
		RequestBase.__init__(self)
		self._api = 'Verify'
		self.__addresses = {}
		return
	
	def addAddress(self, addr_id, usps_addr):
		if len(self.__addresses) >= 5:
			raise ValueError('USPS address verification only allows up to 5 addresses per request.')
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
		root_elem = xd.createElement('AddressValidateRequest')
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

