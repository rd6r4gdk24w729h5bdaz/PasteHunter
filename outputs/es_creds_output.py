from elasticsearch import Elasticsearch
from common import parse_config
from datetime import datetime
import logging
import re

logger = logging.getLogger('pastehunter')
config = parse_config()

class ESCredsOutput():
    def __init__(self):
        # Set up the database connection
        es_host = config['outputs']['es_creds_output']['elastic_host']
        es_port = config['outputs']['es_creds_output']['elastic_port']
        es_user = config['outputs']['es_creds_output']['elastic_user']
        es_pass = config['outputs']['es_creds_output']['elastic_pass']
        self.es_index = config['outputs']['es_creds_output']['elastic_index']
        self.weekly = config['outputs']['es_creds_output']['weekly_index']
        es_ssl = config['outputs']['es_creds_output']['elastic_ssl']
        self.test = False
        try:
            self.es = Elasticsearch(es_host, port=es_port, http_auth=(es_user, es_pass), use_ssl=es_ssl)
            self.test = True
        except Exception as e:
            logger.error(e)
            raise Exception('Unable to Connect') from None
        self.email_password_regex = re.compile('(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(\s*[:\|;]\s*)(?P<password>\w*)')

    def store_paste(self, paste_data):
        if not self.test:
            logger.error("Elastic Search Enabled, not configured!")
            return

        index_name = self.es_index
        if self.weekly:
            year_number = datetime.date(datetime.now()).isocalendar()[0]
            week_number = datetime.date(datetime.now()).isocalendar()[1]
            index_name = '{0}-{1}-{2}'.format(index_name, year_number, week_number)

        # Extract creds from paste
        cred_counter = 0
        for line in paste_data['raw_paste'].splitlines():
            res = self.email_password_regex.match(line)
            if res:
                cred = {'email':    res.group("email"),
                        'password': res.group("password")
                        }
                res = self.es.index(index=index_name, doc_type='email_password', body=cred)
                logger.debug("index res= {0}".format(res))
                cred_counter += 1

        logger.debug("{0} credentials were found".format(cred_counter))
