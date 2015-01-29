import urllib2, urllib
import json
import time
import mimetools, mimetypes
import os, stat
import random
import string

class Callable:
	def __init__(self, anycallable):
		self.__call__ = anycallable

class MultipartPostHandler(urllib2.BaseHandler):
	handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first
	def http_request(self, request):
		data = request.get_data()
		doseq = 1
		if data is not None and type(data) != str:
			v_files = []
			v_vars = []
			try:
				 for(key, value) in data.items():
					 if str(type(value)) == "<type 'file'>":
						 v_files.append((key, value))
					 else:
						 v_vars.append((key, value))
			except TypeError:
				systype, value, traceback = sys.exc_info()
				raise TypeError, "not a valid non-string sequence or mapping object", traceback

			if len(v_files) == 0:
				data = urllib.urlencode(v_vars, doseq)
			else:
				boundary, data = self.multipart_encode(v_vars, v_files)
				contenttype = 'multipart/form-data; boundary=%s' % boundary
				if(request.has_header('Content-Type')
				   and request.get_header('Content-Type').find('multipart/form-data') != 0):
					print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
				request.add_unredirected_header('Content-Type', contenttype)

			request.add_data(data)
		return request

	def multipart_encode(vars, files, boundary = None, buffer = None):
		if boundary is None:
			boundary = mimetools.choose_boundary()
		if buffer is None:
			buffer = ''
		for(key, value) in vars:
			buffer += '--%s\r\n' % boundary
			buffer += 'Content-Disposition: form-data; name="%s"' % key
			buffer += '\r\n\r\n' + value + '\r\n'
		for(key, fd) in files:
			file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
			filename = fd.name.split('/')[-1]
			contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
			buffer += '--%s\r\n' % boundary
			buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
			fd.seek(0)
			buffer += '\r\n' + fd.read() + '\r\n'
		buffer += '--%s--\r\n\r\n' % boundary
		return boundary, buffer
	multipart_encode = Callable(multipart_encode)
	https_request = http_request

def upload(file):
	opener = urllib2.build_opener(MultipartPostHandler)
	opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0')]
	while True:
		try:
			key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
			data = opener.open("https://gifaffe.s3.amazonaws.com/", {'file': open(file, "rb"),'key':key,'acl':'private','AWSAccessKeyId': 'AKIAIT4VU4B7G2LQYKZQ','policy': 'eyAiZXhwaXJhdGlvbiI6ICIyMDIwLTEyLTAxVDEyOjAwOjAwLjAwMFoiLAogICAgICAgICAgICAiY29uZGl0aW9ucyI6IFsKICAgICAgICAgICAgeyJidWNrZXQiOiAiZ2lmYWZmZSJ9LAogICAgICAgICAgICBbInN0YXJ0cy13aXRoIiwgIiRrZXkiLCAiIl0sCiAgICAgICAgICAgIHsiYWNsIjogInByaXZhdGUifSwKCSAgICB7InN1Y2Nlc3NfYWN0aW9uX3N0YXR1cyI6ICIyMDAifSwKICAgICAgICAgICAgWyJzdGFydHMtd2l0aCIsICIkQ29udGVudC1UeXBlIiwgIiJdLAogICAgICAgICAgICBbImNvbnRlbnQtbGVuZ3RoLXJhbmdlIiwgMCwgNTI0Mjg4MDAwXQogICAgICAgICAgICBdCiAgICAgICAgICB9','success_action_status':'200','signature': 'mk9t/U/wRN4/uU01mXfeTe2Kcoc=','Content-Type':'image/gif'}).read()
			print data
			break
		except urllib2.HTTPError as e:
			print e
			time.sleep(10)
	print "Gif uploaded. Key: "+key
	while True:
		try:
			req = opener.open('http://upload.gfycat.com/transcode/'+key).read()
			jsonreq = json.loads(req)
			print "Gfycat link: http://gfycat.com/"+jsonreq["gfyId"]
			return "http://gfycat.com/"+jsonreq["gfyId"]
			break
		except urllib2.HTTPError as e:
			print e
			time.sleep(10)
