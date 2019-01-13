# ToDo
* Handle these kind of credentials:
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
