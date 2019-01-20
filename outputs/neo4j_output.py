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
        self.leak_regex = re.compile('(?P<email>(?P<username>[a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.)*(?P<domain>[a-zA-Z0-9-\.]+)\.(?P<tld>[a-zA-Z0-9]+))(\s*[:\|;]*\s*)(?P<password>.+?)[:\|;\s]')
        self.test = False
        try:
            self.db = GraphDatabase("http://{0}:{1}".format(neo4j_host, neo4j_port), neo4j_user, neo4j_pass)
            self.test = True
        except Exception as e:
            logger.error(e)
            raise Exception('Unable to Connect') from None

    def store_paste(self, paste_data):
        if not self.test:
            logger.error("Neo4j Enabled, not configured!")
            return

        # Extract creds from paste
        cred_counter = 0
        for line in paste_data['raw_paste'].splitlines():
            logger.debug("Line: '{0}' ".format(line))
            res = self.leak_regex.match(line+os.linesep)
            logger.debug("regex res: {0} ".format(res))
            if res:
                cred = {'email': res.group("email").lower(),
                        'username': res.group("username").lower(),
                        'domain': res.group("domain").lower(),
                        'tld': res.group("tld").lower(),
                        'password': res.group("password")
                        }
                logger.debug("Leak: {0} ".format(cred))

                # Format dict to neo4j "json"
                neo4j_json = ''
                for key, value in cred.items():
                    neo4j_json += "{0}: '{1}', ".format(key, value)
                neo4j_json = neo4j_json[:-2]  # Remove trailing ", "

                # Format neo4j "json" to Neo4j Cypher "create and update"
                db_insert = "MERGE (:email_password_leak {{ {0} }})".format(neo4j_json)
                logger.debug("Cypher: {0} ".format(db_insert))

                # Insert in DB
                self.db.query(db_insert)
                cred_counter += 1

        logger.info("Paste {0} contains {1} email password leak".format(paste_data["pasteid"], cred_counter))
