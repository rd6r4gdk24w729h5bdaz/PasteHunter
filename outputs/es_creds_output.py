from elasticsearch import Elasticsearch
from common import parse_config
from datetime import datetime
import logging

logger = logging.getLogger('pastehunter')
config = parse_config()

class ESCredsOutput():
    def __init__(self):
        # Set up the database connection
        es_host = config['outputs']['elastic_output']['elastic_host']
        es_port = config['outputs']['elastic_output']['elastic_port']
        es_user = config['outputs']['elastic_output']['elastic_user']
        es_pass = config['outputs']['elastic_output']['elastic_pass']
        self.es_index = config['outputs']['elastic_output']['elastic_index']
        self.weekly = config['outputs']['elastic_output']['weekly_index']
        es_ssl = config['outputs']['elastic_output']['elastic_ssl']
        self.test = False
        try:
            self.es = Elasticsearch(es_host, port=es_port, http_auth=(es_user, es_pass), use_ssl=es_ssl)
            self.test = True
        except Exception as e:
            logger.error(e)
            raise Exception('Unable to Connect') from None

    def store_paste(self, paste_data):
        if self.test:
            index_name = self.es_index
            if self.weekly:
                year_number = datetime.date(datetime.now()).isocalendar()[0]
                week_number = datetime.date(datetime.now()).isocalendar()[1]
                index_name = '{0}-{1}-{2}'.format(index_name, year_number, week_number)

            # Extract creds from paste
            logger.debug("###################################################")
            logger.debug("PasteId={0}", format(paste_data['pasteid']))
            logger.debug("PasteSite={0}", format(paste_data['pastesite']))
            logger.debug("YaraRules={0}", format(paste_data['YaraRule']))
            cred_counter = 0
            email_password_regex = r'(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)([:\|;])(?P<password>\w*)'

            for line in paste_data['raw_paste'].splitlines():
                res = email_password_regex.match(line)
                if res:
                    cred = {'email':    res.group("email"),
                            'password': res.group("password")
                            }
                    logger.debug("    email={0} password={1}", format(cred['email'], cred['password']))
                    self.es.index(index=index_name, doc_type='paste', body=cred)
                    cred_counter += 1

            logger.debug("cred_counter={0}", format(cred_counter)
