#!/usr/bin/env python
'''
File			:	utility.py
Package			:	usps_webtools
Brief			:	Utility functions used in the usps_webtools Python package.
Author			:	William M. Clifford
--------------------------------------------------------------------------------
'''

import libxml2
import sys
import xml.dom.minidom

#-------------------------------------------------------------------------------
# function: createXmlElement(parent_element, new_element_name, new_element_value)
#
# Description:
# Used to create and append an XML element into the DOM tree beneath the given
# parent element. Find myself doing this a lot when building the various
# request XML documents.
#
# <parent_element>
#   ... other child elements ...
#   <new_element_name>new_element_value</new_element_name>
# </parent_element>
#
# Params:
# parent_element - a DOM node
# new_element_name - string; name of new child element
# new_element_value - string; content of new child element
#
# Returns:
# the newly-created XML element
#
#-------------------------------------------------------------------------------
def createXmlElement(parent_element, new_element_name, new_element_value):
	'''
	Used to create and append an XML element into the DOM tree beneath the
	given parent element.
	'''
	xd = parent_element.ownerDocument
	elem = xd.createElement(new_element_name)
	if elem:
		if new_element_value:
			elem.appendChild(xd.createTextNode(new_element_value))
		parent_element.appendChild(elem)
		pass
	return elem

#-------------------------------------------------------------------------------
# function: getXmlElement(xpath_ctx, xpath_query_txt)
#
# Description:
# Utility function that will perform the XPATH query in the given context,
# returning either the first matching XML element or None if the query returns
# no results. This gets used frequently when parsing the XML responses received
# from the USPS server.
#
# Params:
#	xpath_ctx - XPATH context object
#	xpath_query_txt - string; XPATH query string requesting a particular XML
#		element within the given XPATH context
#
# Returns:
#	The first XML element matching the XPATH query, or None where query returns
#	no results.
#
#-------------------------------------------------------------------------------
def getXmlElement(xpath_ctx, xpath_query_txt):
	'''
	Utility function that will perform the XPATH query in the given context,
	returning either the first matching XML element or None if the query returns
	no results.
	'''
	elem = None
	#
	try:
		qry_results = xpath_ctx.xpathEval(xpath_query_txt)
		if qry_results:
			elem = qry_results[0]
		pass
	except Exception, ex:
		sys.stderr.write('getXmlElement(): exception - %s\n' % str(ex))
		elem = None
		pass
	return elem

#-------------------------------------------------------------------------------
# function: getXmlElementContents(xpath_ctx, xpath_query_txt, default_value='')
#
# Description:
# Utility function that will perform the XPATH query in the given context,
# returning the contents of the first matching XML element or the given default
# value if the query returns no results.
#
# Params:
#	xpath_ctx - XPATH context object
#	xpath_query_txt - string; XPATH query string requesting a particular XML
#		element within the given XPATH context
#	default_value - string; the value to be returned when the XPATH query does
#		not return any results. Default: ""
#
# Returns:
#	The contents of the first XML element matching the XPATH query, or the
#	default value where the query returns no results.
#
#-------------------------------------------------------------------------------
def getXmlElementContents(xpath_ctx, xpath_query_txt, default_value=''):
	'''
	Utility function that will perform the XPATH query in the given context,
	returning the contents of the first matching XML element or the given default
	value if the query returns no results.
	'''
	elem = getXmlElement(xpath_ctx, xpath_query_txt)
	if elem:
		return elem.content
	return default_value
