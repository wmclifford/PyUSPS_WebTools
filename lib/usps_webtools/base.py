#!/usr/bin/env python
'''
File			:	base.py
Package			:	usps_webtools
Brief			:	Base classes used for implementing the request/response
					model for each of the USPS APIs.
Author			:	William M. Clifford
--------------------------------------------------------------------------------
'''

import libxml2
import urllib

#-------------------------------------------------------------------------------
# class: ResponseBase
#
# Description:
# Base response class. All of the response handling classes in the usps_webtools
# package and its subpackages should derive from this class, implementing the
# _parseElement() method.
#
# Public methods:
#	None
#
# Protected methods:
#	_parseElement(elem)
#		Parses the provided XML element, populating the fields of the response
#		object with the data in the XML element and its child nodes. Since
#		each response object will expose different kinds of data, this base
#		interface is left abstract.
#
#-------------------------------------------------------------------------------
class ResponseBase(object):
	
	def _parseElement(self, elem):
		'''
		Parses the provided XML element, filling the fields of the object with
		the data in the XML element.
		'''
		pass
	
	pass

# Forward declaration of the ErrorResponse class, based on ResponseBase.
from usps_webtools.errors import ErrorResponse

# Utility function used to parse out XPATH elements from the response XML.
from usps_webtools.utility import getXmlElement

#-------------------------------------------------------------------------------
# class: RequestBase
#
# Description:
#
# Public properties:
#
#	OPERATION_MODE - string; "TEST" or "PRODUCTION" (static)
#
#	RESPONSE_CLASS - class; the ResponseBase descendant that will interpret the
#		response given by the USPS server. (static)
#
#	SERVER_REQUEST_URI - string; the URI to which the request will be sent.
#		This should be the complete URI, including the http:/https: prefix.
#		Note that this will be modified according to the value of OPERATION_MODE
#		to adjust whether the request goes to the production server or the
#		test server. (static)
#
#	xml - string; the XML request as a string.
#
# Public methods:
#
#	submit()
#		Submits the request to the USPS webserver, posting the API and XML
#		request text, and uses an instance of the RESPONSE_CLASS class to
#		interpret the response received from the server.
#
# Protected properties:
#
#	_api - string; the name of the API that the USPS server is supposed to use
#		to process the request.
#
# Protected methods:
#
#	_constructDOM()
#		Constructs the XML DOM document that describes the contents of the
#		Request instance. This is utilized by the xml property, calling
#		_constructDOM() to make the XML DOM object from which the toxml()
#		method is used to get the XML text string.
#
#-------------------------------------------------------------------------------
class RequestBase(object):
	
	# The URI to which the request will be made.
	SERVER_REQUEST_URI = ''
	
	# The ResponseBase descendant associated with this request object.
	# This is the class itself, not its name (i.e. MyResponseClass not
	# "MyResponseClass").
	RESPONSE_CLASS = None
	
	# Operating in TEST or PRODUCTION mode.
	OPERATION_MODE = 'PRODUCTION'
	
	def __init__(self):
		self._api = ''
		return
	
	def submit(self):
		'''
		Submits the request to the USPS webserver, posting the API and XML
		request text, and uses an instance of the RESPONSE_CLASS class to
		interpret the response received from the server.
		'''
		resp_obj = None
		post_data = urllib.urlencode({
			'API': self._api,
			'XML': self.xml,
			})
		try:
			req_uri = self.SERVER_REQUEST_URI
			if self.OPERATION_MODE == 'TEST':
				req_uri = req_uri.replace('API.dll', 'APITest.dll')
				if req_uri.startswith('https:'):
					req_uri = req_uri.replace('production', 'secure')
				else:
					req_uri = req_uri.replace('production', 'testing')
				sys.stderr.write('TESTING MODE := ON\nRequest URI := %s\n' % req_uri)
				sys.stderr.write('Post data := %s\n' % str(post_data))
				sys.stderr.write('self.xml := %s\n' % self.xml)
				pass
			url_handle = urllib.urlopen(req_uri, post_data)
			resp_txt = url_handle.read()
			url_handle.close()
			# Dump the XML response if testing.
			if self.OPERATION_MODE == 'TEST':
				sys.stderr.write('Response text:\n%s\n' % resp_txt)
				pass
			pass
		except Exception, ex:
			sys.stderr.write('Unable to retrieve request: %s\n' % str(ex))
			return None
		# Parse the response text into a response object.
		try:
			# The response class should be identified by the request class
			# using the RESPONSE_CLASS class-level value.
			xd = libxml2.parseMemory(resp_txt, len(resp_txt))
			ctx = xd.xpathNewContext()
			# Check for an error response as the root of the XML document.
			root_elem = getXmlElement(ctx, '/*')
			if root_elem:
				# Check to see if the root element is <Error>
				if root_elem.name.upper() == 'ERROR':
					resp_obj = ErrorResponse(root_elem)
				else:
					resp_obj = self.RESPONSE_CLASS(root_elem)
				pass
			# At this point the response object has parsed the XML text.
			# Release the libxml2 XML document.
			xd.freeDoc()
			ctx.xpathFreeContext()
			pass
		except Exception, ex:
			sys.stderr.write('Unable to parse response text: %s\n' % str(ex))
			return None
		return resp_obj
	
	@property
	def xml(self):
		'''Returns the request as an XML string, constructing it from the
		properties of the Request class instance.'''
		xd = self._constructDOM()
		xml_string = xd.toxml()
		xd.unlink()
		return xml_string
	
	def _constructDOM(self):
		'''Constructs the XML DOM document that describes the contents of the
		Request instance.'''
		pass
	
	pass

