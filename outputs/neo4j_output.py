from neo4jrestclient.client import GraphDatabase
from common import parse_config
import logging
import re
import os

logger = logging.getLogger('pastehunter')
config = parse_config()


class Neo4jOutput():
    def __init__(self):
        # Set up the database connection
        neo4j_host = config['outputs']['neo4j_output']['neo4j_host']
        neo4j_port = config['outputs']['neo4j_output']['neo4j_port']
        neo4j_user = config['outputs']['neo4j_output']['neo4j_user']
        neo4j_pass = config['outputs']['neo4j_output']['neo4j_pass']
        self.test = False
        try:
            self.db = GraphDatabase("http://{0}:{1}".format(neo4j_host, neo4j_port), neo4j_user, neo4j_pass)
            self.test = True
        except Exception as e:
            logger.error(e)
            raise Exception('Unable to Connect') from None
        self.username_password_regex = re.compile('(?P<username>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(\s*[:\|;]\s*)(?P<password>.+?)[:\|;\s]')

    def store_paste(self, paste_data):
        if not self.test:
            logger.error("Neo4j Enabled, not configured!")
            return

        # Extract creds from paste
        cred_counter = 0
        for line in paste_data['raw_paste'].splitlines():
            logger.debug("Line: {0} ".format(line))
            res = self.username_password_regex.match(line+os.linesep)
            logger.debug("res: {0} ".format(res))
            if res:
                cred = {'username': res.group("username"),
                        'password': res.group("password")
                        }
                logger.debug("Cred: {0} ".format(cred))

                # Format dict to neo4j "json"
                neo4j_json = ''
                for key, value in cred.items():
                    neo4j_json += "{0}: '{1}', ".format(key, value)
                neo4j_json = neo4j_json[:-2]  # Remove trailing ", "
                logger.debug("neo4j_json: {0} ".format(neo4j_json))

                # Insert in DB
                db_insert = "MERGE (:username_password {{ {0} }})".format(neo4j_json)
                logger.debug("Cypher: {0} ".format(db_insert))
                self.db.query(db_insert)
                cred_counter += 1

        logger.info("Paste {0} contains {1} username password credentials".format(paste_data["pasteid"], cred_counter))
