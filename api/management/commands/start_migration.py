import os
from django.core.management.base import BaseCommand
from django.conf import settings
from time import time
from api.utils.process import handle_file, process_data

BASE_DIR = settings.BASE_DIR



class Command(BaseCommand):
	help = "Send message to customers who has payment for today"

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str, help='path to the input file')		

	def handle(self, *args, **options):
		start_time = time()
		filename = options['file'][0]

		if not os.path.isfile(filename):
			raise ValueError("Input file %s does not exist" % filename)

		if filename.split('.')[-1] == '.xlsx':
			raise ValueError("Invalid file type: %s\nOnly xlsx type supported" % filename)

		product_list = handle_file(filename)
		process_data(product_list)
		end_time = time()
		
		self.stdout.write(f'finished: {end_time - start_time} seconds')
		self.stdout.write(self.style.SUCCESS(f'All data migrated successfully: {filename}'))