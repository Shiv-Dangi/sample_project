#!/usr/bin/python

from ccavutil import encrypt,decrypt
from string import Template
from django.http import HttpResponse

def res(encResp):
	'''
	Please put in the 32 bit alphanumeric key in quotes provided by CCAvenues.
	'''	 
	workingKey = 'F06C47C78E0542A1CBDAABC6D0E99634'
	decResp = decrypt(encResp,workingKey)
	data = '<table border=1 cellspacing=2 cellpadding=2><tr><td>'	
	data = data + decResp.replace('=','</td><td>')
	data = data.replace('&','</td></tr><tr><td>')
	data = data + '</td></tr></table>'
	
	html = '''\
	<html>
		<head>
			<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
			<title>Response Handler</title>
		</head>
		<body>
			<center>
				<font size="4" color="blue"><b>Response Page</b></font>
				<br>
				$response
			</center>
			<br>
		</body>
	</html>
	'''
	fin = Template(html).safe_substitute(response=data)
	return HttpResponse(fin)
