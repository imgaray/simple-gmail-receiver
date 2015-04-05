# -*- coding: utf-8 -*-

import imaplib
import configparser
import os
import sys
import email
import base64

non_valid_charset = '@.,_<>$%&=\\/¿!|°+´^~¬`:;+*{}[]\n\r\t'

non_valid_charmap = {ord(key): None for key in non_valid_charset}

class Configuration(object):

	section = "GLOBAL"
	
	def __init__(self, config_file_name):
		self.file_name = config_file_name
		self.parser = configparser.ConfigParser()
		self.parser.read(os.path.join(os.path.dirname(sys.argv[0]), self.file_name))

	def __getitem__(self, key):
		return self.parser.get(Configuration.section, key)

class GmailClient(object):
	
	GMAIL_HOSTNAME = "imap.gmail.com"
	
	def __init__(self, username, password):
		self.connection = imaplib.IMAP4_SSL(GmailClient.GMAIL_HOSTNAME)
		self.username = username
		self.password = password
		self.connection.login(self.username, self.password)
		
	def search(self, criteria):
		search_result = self.connection.search(None, criteria)
		return search_result[0], [id.decode('utf-8') for id in search_result[1][0].split()]
		
	def fetch_iterator(self, messages_ids):
		if messages_ids is None or len(messages_ids) == 0:
			raise StopIteration
		for id in messages_ids:
			status, response = self.connection.fetch(id, '(RFC822)')
			yield RawResponse(status, response)
	
	def fetch_one(self, id):
		status, response = self.connection.fetch(id, '(RFC822)')
		return RawResponse(status, response)
	
	def set_mailbox(self, mailbox):
		self.connection.select(mailbox)
	
	def list(self):
		return self.connection.list()
	
	def close(self):
		self.connection.close()
		
	def logout(self):
		self.connection.logout()

class RawResponse:
	def __init__(self, status, data):
		self.status = status
		self.data = data
		
	def parsed_mail(self):
		return email.message_from_bytes(self.data[0][1] )

	def is_ok(self):
		return self.status == "OK"
	
	def create_dir_if_unexistant(self, filename):
		if not os.path.exists(filename):
			os.mkdir(filename)
	
	def save_to_file(self):
		rootDir = configuration["rootDir"]
		mail = self.parsed_mail()
		fromHeader = str(email.header.make_header(email.header.decode_header(mail["From"])))
		subjectHeader = str(email.header.make_header(email.header.decode_header(mail["Subject"])))
		print("From:", fromHeader)
		print("Subject:", subjectHeader)
		senderDir = os.path.join(rootDir, fromHeader.translate(non_valid_charmap))
		self.create_dir_if_unexistant(senderDir)
		currentMailDir = os.path.join(senderDir, subjectHeader.translate(non_valid_charmap))
		self.create_dir_if_unexistant(currentMailDir)
		for part in mail.walk():
			if part.get_content_maintype() == 'multipart':
				continue
			if part.get('Content-Disposition') is None:
				continue
			filename = str(email.header.make_header(email.header.decode_header(part.get_filename())))
			att_path = os.path.join(currentMailDir, filename)
			try:
				with open(att_path, 'wb') as out:
					out.write(base64.b64decode(part.get_payload()))
			except TypeError:
				with open(att_path, 'wb') as out:
					out.write(part.get_payload())
	
configuration = Configuration("config")
		
def main():
	username = configuration["username"]
	password = configuration["password"]
	print("logging in as", username)
	client = GmailClient(username, password)
	client.set_mailbox(configuration["mailbox"])
	filter = create_filter_search()
	print("filter", filter)
	status, ids = client.search(create_filter_search())
	print("ids:", ids)
	if status == "OK":
		for id in ids:
			process_mail(client, id)
	client.close()
	client.logout()
	
def create_filter_search():
	return configuration["filter"]

def process_mail(client, id):
	rawResponse = client.fetch_one(id)
	if not rawResponse.is_ok():
		return
	rawResponse.save_to_file()
	
if __name__ == "__main__":
	main()