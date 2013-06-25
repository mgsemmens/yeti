######################################################################################
#                                                                                    #
# Copyright (C) 2012-2013 - The MITRE Corporation. All Rights Reserved.              #
#                                                                                    #
# By using the software, you signify your aceptance of the terms and                 #
# conditions of use. If you do not agree to these terms, do not use the software.    #
#                                                                                    #
# For more information, please refer to the license.txt file.                        #
#                                                                                    #
######################################################################################

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
import datetime
from dateutil.tz import tzutc
import validators
import settings

#Certificate table for certificate management
class Certificate(models.Model):
	#id is an Autogenerated field
	title = models.CharField(max_length=64)
	description = models.TextField(blank=True)
	subject = models.CharField(max_length=255, unique=True, editable=False, default='Unassigned')
	issuer = models.CharField(max_length=255, editable=False, default='Unassigned')
	pem_certificate = models.TextField(validators=[validators.CertificateValidator])
	created = models.DateTimeField(default=lambda:datetime.datetime.now(tzutc()))
	
	def __unicode__(self):
		return self.title
	
	def clean(self):
		from django.core.exceptions import ValidationError
		import OpenSSL
		x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, self.pem_certificate)
		x509subject = x509.get_subject()
		self.subject = str(x509subject)[18:-2]
		x509issuer = x509.get_issuer()
		self.issuer = str(x509issuer)[18:-2]

def do_export_certs(sender, **kwargs):
	export_location = settings.CERT_EXPORT_LOCATION
	export_file = open(export_location, 'w')
	all_certs = Certificate.objects.all()
	for cert in all_certs:
		export_file.write(cert.pem_certificate + '\r\n')
	export_file.flush()
	export_file.close()
	return

post_save.connect(do_export_certs, sender=Certificate)
post_delete.connect(do_export_certs, sender=Certificate)

