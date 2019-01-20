from neo4jrestclient.client import GraphDatabase
from common import parse_config
import logging
import json
import re
import os

logger = logging.getLogger('pastehunter')
config = parse_config()

'''
# Some usefull queries

    //Full text search for $SEARCH
        match (n) where (any(prop in keys(n) where n[prop] =~ ".*$SEARCH.*")) return n
    //TLD stats
        match (n) return n.tld, count(n.tld) as count order by count desc
'''

class Neo4jOutput():
    def __init__(self):
        self.debug_mode = config['outputs']['neo4j_output']['debug_mode']

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

        self.must_store_paste = config['outputs']['neo4j_output']['must_store_paste']
        self.must_store_credential = config['outputs']['neo4j_output']['must_store_credential']

        self.credential_regex = re.compile('(?P<email>(?P<username>[a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.)*(?P<domain>[a-zA-Z0-9-\.]+)\.(?P<tld>[a-zA-Z0-9]+))((\s|[,:;|│])+)(?P<password>.+?)((\s|[,:;|│]|<br>)+)')

    def merge(self, dict, nodetype):
        # Format dict to neo4j "json"
        neo4j_json = ''
        for key, value in dict.items():
            key = key.replace("@", "")
            if not isinstance(value,(str,)):
                value = json.dumps(value)
            value = value.replace("'", "\\'")
            value = value.replace('"', '\\"')
            value = value.replace("\\", "\\\")
            neo4j_json += "{0}: '{1}', ".format(key, value)
        neo4j_json = neo4j_json[:-2]  # Remove trailing ", "

        # Format neo4j "json" to Neo4j Cypher "create and update"
        db_insert = "MERGE (:{0} {{ {1} }})".format(nodetype, neo4j_json)
        logger.debug("Cypher: {0} ".format(db_insert))

        # Insert in DB
        self.db.query(db_insert)

    def extract_credential(self, paste_data):
        # Extract creds from paste
        credential_count = 0
        for line in paste_data['raw_paste'].splitlines():
            logger.debug("Line: '{0}' ".format(line))
            res = self.credential_regex.match(line+os.linesep)
            logger.debug("regex match: {0} ".format(res))
            if res:
                cred = {'email': res.group("email").lower(),
                        'username': res.group("username").lower(),
                        'domain': res.group("domain").lower(),
                        'tld': res.group("tld").lower(),
                        'password': res.group("password"),
                        'line': line,
                        }
                logger.debug("Credential: {0} ".format(cred))
                self.merge(cred, "credential")
                credential_count += 1
        logger.info("Paste {0} contains {1} credential leaks".format(paste_data["pasteid"], credential_count))

    def store_paste(self, paste_data):
        try:
            if not self.test:
                logger.error("Neo4j Enabled, not configured!")
                return

            if self.must_store_credential:
                self.extract_credential(paste_data)

            if self.must_store_paste:
                self.merge(paste_data, "paste")
        except Exception as e:
            if self.debug_mode:
                logger.debug("FAILLURE at {0} with error {1} ######################################################################################################################################".format(paste_data["pasteid"], e))
                os.system('halt'
            else:
                raise e
