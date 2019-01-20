# ToDo
* For Neo4j, insert pastes and link them to username_passwords.
* ensure those formats are found by the username_password_regex or a second step regex.
  * MyPassword123 test123@hotmail.com
  * As Combo: test123@hotmail.com:MyPassword123
* for each email, extract and store tld, org (domain without tld), and username (email without @org.tld) so search is easier on ES
* The waitoforit.sh script used in the dockerfile sucks.
  If we disable ES from active outputs, we never run the container...
  We need to replace it by a small check at output initialisation like this one:

  >  # Connect to DB
  >  connection_try=0
  >  while True:
  >    try:
  >      connection_try += 1
  >      db = GraphDatabase(db_endpoint, db_username, db_password)
  >      log("Connected to DB (try "+str(connection_try)+"/"+str(max_connection_try)+")","debug")
  >      break
  >    except:
  <      log("Not connected to DB (try "+str(connection_try)+"/"+str(max_connection_try)+")","warning")
  >      if connection_try >= max_connection_try:
  <        log("DB unrecheable. Aborting...","error")
  >        exit(1)
  >      time.sleep(connection_delay)

* Handle these kind of credentials:
  * ovpn
  * cisco passwords in a cisco_password index
    "enable secret" wide ascii nocase
    "enable password" wide ascii nocase
    with domain, hostname, password
  * private keys in a private_key index
    $ssh_priv = "BEGIN RSA PRIVATE KEY" wide ascii nocase
    $openssh_priv = "BEGIN OPENSSH PRIVATE KEY" wide ascii nocase
    $dsa_priv = "BEGIN DSA PRIVATE KEY" wide ascii nocase
    $ec_priv = "BEGIN EC PRIVATE KEY" wide ascii nocase
    $pgp_priv = "BEGIN PGP PRIVATE KEY" wide ascii nocase
    $pem_cert = "BEGIN CERTIFICATE" wide ascii nocase
    $pkcs7 = "BEGIN PKCS7"
    with ????
  * twitter_api
    strings:
      $a = "consumer_key" nocase
      $b = "consumer_secret" nocase
      $c = "access_token" nocase
    condition:
      all of them
  * google_api
        $a = /\bAIza.{35}\b/
  * github_api
      $a = /[g|G][i|I][t|T][h|H][u|U][b|B].*[[\'|"]0-9a-zA-Z]{35,40}[\'|"]/
  * aws_api
    $a = /AKIA[0-9A-Z]{16}/
  * connection_string
    $a = /\b(mongodb|http|https|ftp|mysql|postgresql|oracle):\/\/(\S*):(\S*)@(\S*)\b/
