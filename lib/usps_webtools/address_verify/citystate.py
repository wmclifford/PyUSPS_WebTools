#!/usr/bin/env python
'''
File			:	citystate.py
Package			:	usps_webtools.address_verify
Brief			:	Implements the city/state lookup request/response model.
Author			:	William M. Clifford
--------------------------------------------------------------------------------
'''

import os
import xml.dom.minidom

USPS_USER_ID = os.environ['USPS_USER_ID']

# Import the base request and response objects.
from usps_webtools.base import RequestBase, ResponseBase

# Grab the utility functions
from usps_webtools.utility import createXmlElement, getXmlElement, getXmlElementContents

#-------------------------------------------------------------------------------
# class: USPSZipCode
#-------------------------------------------------------------------------------
class USPSZipCode(object):
	
	def __init__(self, **kw):
		self.city = kw.get('city', '')
		self.state = kw.get('state', '')
		self.zip5 = kw.get('zip5', '')
		return
	
	@property
	def city(self):
		return self.__city
	@city.setter
	def city(self, value):
		if value is None:
			self.__city = ''
		else:
			self.__city = str(value).strip()
		return
	
	@property
	def state(self):
		return self.__state
	@state.setter
	def state(self, value):
		if value is None:
			self.__state = ''
		else:
			self.__state = str(value).strip()
		return
	
	@property
	def zip5(self):
		return self.__zip5
	@zip5.setter
	def zip5(self, value):
		if value is None:
			self.__zip5 = ''
		else:
			self.__zip5 = str(value).strip()
		return
	
	def parseFromXML(self, xmlpath_ctx):
		'''
		Uses XPATH to parse the contents of an XML node and populate the
		field values with the data therein.
		'''
		if not xmlpath_ctx:
			return
		if xmlpath_ctx.name != 'ZipCode':
			# Not an <ZipCode></ZipCode> element.
			return
		for elemName in ('City', 'State', 'Zip5'):
			fieldName = elemName[0].lower() + elemName[1:]
			try:
				fieldValue = getXmlElementContents(xmlpath_ctx, './%s' % elemName)
				self.__setattr__(fieldName, fieldValue)
				pass
			except Exception, ex:
				sys.stderr.write('USPSZipCode.parseFromXML(): Failed to parse element %s from XML.\n\t%s\n' % (elemName, str(ex)))
				pass
			pass
		return
	
	pass

#-------------------------------------------------------------------------------
# class: CityStateLookupResponse
#-------------------------------------------------------------------------------
class CityStateLookupResponse(ResponseBase):
	
	def __init__(self, xmlElement):
		ResponseBase.__init__(self)
		self.__addresses = []
		self._parseElement(xmlElement)
		return
	
	def __str__(self):
		s = ('=' * 72) + '\nUSPS City State Lookup - Response\n' + ('=' * 72) + '\n'
		for k, v in self.__addresses:
			s += 'ZIP CODE ID "%s"\n' % k
			s += str(v)
			pass
		return s
	
	@property
	def addresses(self):
		return tuple(self.__addresses)
	
	def _parseElement(self, elem):
		# elem is the XPATH context for the root element
		try:
			root_element = getXmlElement(elem, '/CityStateLookupResponse')
		except Exception:
			sys.stderr.write('CityStateLookupResponse._parseElement(): XML document root element is not of expected value.\n')
			sys.stderr.write('\tExpecting "<CityStateLookupResponse>", got "<%s>".\n' % elem.name)
			return
		# Get each of the addresses that were validated.
		for addr_elem in elem.xpathEval('/CityStateLookupResponse/ZipCode'):
			addr_id = addr_elem.prop('ID')
			usps_addr = USPSZipCode()
			usps_addr.parseFromXML(addr_elem)
			self.__addresses.append( (addr_id, usps_addr) )
			pass
		return
	
	pass

#-------------------------------------------------------------------------------
# class: CityStateLookupRequest
#-------------------------------------------------------------------------------
class CityStateLookupRequest(RequestBase):
	SERVER_REQUEST_URI = 'http://production.shippingapis.com/ShippingAPI.dll'
	RESPONSE_CLASS = CityStateLookupResponse
	
	def __init__(self):
		RequestBase.__init__(self)
		self._api = 'CityStateLookup'
		self.__addresses = {}
		return
	
	def addAddress(self, addr_id, usps_zipcode):
		if len(self.__addresses) >= 5:
			raise ValueError('USPS city/state lookup only allows up to 5 addresses per request.')
		self.__addresses[addr_id] = usps_zipcode
		return
	
	def clearAddresses(self):
		self.__addresses.clear()
	
	def _constructDOM(self):
		'''
		Constructs the XML DOM document that describes the contents of the
		Request instance.
		'''
		xd = xml.dom.minidom.Document()
		root_elem = xd.createElement('CityStateLookupRequest')
		root_elem.setAttribute('USERID', USPS_USER_ID)
		# We want to add all our addresses.
		addr_ids = self.__addresses.keys()
		addr_ids.sort()
		for addr_id in addr_ids:
			zc_elem = xd.createElement('ZipCode')
			zc_elem.setAttribute('ID', addr_id)
			createXmlElement(zc_elem, 'Zip5', self.__addresses[addr_id])
			pass
		# Don't forget to append the root element, and we're all set.
		xd.appendChild(root_elem)
		return xd
	
	pass
