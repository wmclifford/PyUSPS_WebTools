#!/usr/bin/env python
'''
File			:	usaddress.py
Package			:	usps_webtools.address_verify
Brief			:	Provides a utility class that embodies a US postal address.
Author			:	William M. Clifford
--------------------------------------------------------------------------------
'''

# Grab the utility functions
from usps_webtools.utility import createXmlElement, getXmlElementContents

#-------------------------------------------------------------------------------
# class: USPSAddress
#
# Public properties:
#	address1 - string; apartment or suite number, max 38 chars
#	address2 - string; street address, max 38 chars
#	city - string; max 38 chars
#	firmName - string; company name, max 38 chars (optional)
#	state - string; 2-character abbreviation
#	zip5 - string; 5-digit zip code
#	zip4 - string; the zip+4 4-digit zip code
#
#	Must provide either city & state or zip5 when requesting address
#	verification. Also note that address1 & address2 work backwards from what
#	would normally be expected. address2 contains the street address while
#	address1 is used for apartment or suite numbers.
#
# Public methods:
#	appendToXml(address_id, parent_element)
#		Generates an XML DOM node beneath the given parent node, forming the
#		expected request XML used by the USPS webtools API. The API allows
#		the user to verify up to 5 addresses per request, so an ID must be
#		assigned to each address which will be verified.
#
#	parseFromXML(xmlpath_ctx)
#		Uses XPATH to parse the contents of an XML node and populate the
#		field values with the data therein.
#
#-------------------------------------------------------------------------------
class USPSAddress(object):
	
	def __init__(self, **kw):
		self.address1 = kw.get('address1', '')
		self.address2 = kw.get('address2', '')
		self.city = kw.get('city', '')
		self.firmName = kw.get('firmName', '')
		self.state = kw.get('state', '')
		self.zip4 = kw.get('zip4', '')
		self.zip5 = kw.get('zip5', '')
		return
	
	def __str__(self):
		return '''------------------------------------------------------------------------
	FIRM      : %(_USPSAddress__firmName)s
	ADDRESS 1 : %(_USPSAddress__address1)s
	ADDRESS 2 : %(_USPSAddress__address2)s
	CITY      : %(_USPSAddress__city)s
	STATE     : %(_USPSAddress__state)s
	ZIP       : %(_USPSAddress__zip5)s - %(_USPSAddress__zip4)s
------------------------------------------------------------------------
''' % self.__dict__
	
	@property
	def address1(self):
		return self.__address1
	@address1.setter
	def address1(self, value):
		if value is None:
			self.__address1 = ''
		else:
			self.__address1 = str(value).strip()
		return
	
	@property
	def address2(self):
		return self.__address2
	@address2.setter
	def address2(self, value):
		if value is None:
			self.__address2 = ''
		else:
			self.__address2 = str(value).strip()
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
	def firmName(self):
		return self.__firmName
	@firmName.setter
	def firmName(self, value):
		if value is None:
			self.__firmName = ''
		else:
			self.__firmName = str(value).strip()
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
	def zip4(self):
		return self.__zip4
	@zip4.setter
	def zip4(self, value):
		if value is None:
			self.__zip4 = ''
		else:
			self.__zip4 = str(value).strip()
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
	
	def appendToXml(self, address_id, parent_element):
		'''
		Generates an XML DOM node beneath the given parent node, forming the
		expected request XML used by the USPS webtools API. The API allows
		the user to verify up to 5 addresses per request, so an ID must be
		assigned to each address which will be verified.
		'''
		xd = parent_element.ownerDocument
		address_element = xd.createElement('Address')
		address_element.setAttribute('ID', address_id)
		createXmlElement(address_element, 'FirmName', self.__firmName)
		createXmlElement(address_element, 'Address1', self.__address1)
		createXmlElement(address_element, 'Address2', self.__address2)
		createXmlElement(address_element, 'City', self.__city)
		createXmlElement(address_element, 'State', self.__state)
		createXmlElement(address_element, 'Zip5', self.__zip5)
		createXmlElement(address_element, 'Zip4', self.__zip4)
		parent_element.appendChild(address_element)
		return
	
	def parseFromXML(self, xmlpath_ctx):
		'''
		Uses XPATH to parse the contents of an XML node and populate the
		field values with the data therein.
		'''
		if not xmlpath_ctx:
			return
		if xmlpath_ctx.name != 'Address':
			# Not an <Address></Address> element.
			return
		for elemName in ('FirmName', 'Address1', 'Address2', 'City', 'State', 'Zip5', 'Zip4'):
			fieldName = elemName[0].lower() + elemName[1:]
			try:
				fieldValue = getXmlElementContents(xmlpath_ctx, './%s' % elemName)
				self.__setattr__(fieldName, fieldValue)
				pass
			except Exception, ex:
				sys.stderr.write('USPSAddress.parseFromXML(): Failed to parse element %s from XML.\n\t%s\n' % (elemName, str(ex)))
				pass
			pass
		return
	
	pass

