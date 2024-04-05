'''
Module used for the server initialization and configuration.
'''
import flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app.conf_log import conf_logging

webserver = flask.Flask(__name__)
webserver.tasks_runner = ThreadPool()

webserver.tasks_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")
webserver.job_counter = 1

conf_logging(webserver)

webserver.tasks_runner.join()

from app import routes
