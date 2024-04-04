from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
import logging

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

webserver.tasks_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")
webserver.job_counter = 1

from app import routes

webserver.logger = logging.getLogger('webserver.log')
file_handle = logging.FileHandler('webserver.log')
webserver.logger.setLevel(logging.INFO)
webserver.logger.addHandler(file_handle)

webserver.tasks_runner.join()