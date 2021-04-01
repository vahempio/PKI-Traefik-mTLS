# PKI example with client/server authentication

This is a full working example webserver that provides [mTLS](https://en.wikipedia.org/wiki/Mutual_authentication) with [Traefik](https://doc.traefik.io/traefik/).

The example should run in localhost, and all certificates are available (both for server and clients).

The PKI is managed with the excellent [pki-tutorial](https://pki-tutorial.readthedocs.io/en/latest/simple/) example.


# How to test mTLS in 1 minute
## Minimum requirement
Here is the minimal software requirement on your computer:
- docker
- docker-compose
- openssl
- web browser

### Start the server
On the first time, create the network if it does not exist:
```sh
docker network create traefik_network
```
Then start services with:
```sh
docker-compose up
```
and check that the reverse-proxy is up at [http://traefik.localhost](http://traefik.localhost).

On the dashboard, under the tab 'HTTP > Routers', verify that 4 services are up.

### Configure your browser for server auth
Because it is a local test, you need to trust the rootCA certificate (with the public key) of this PKI which have signed the server certificate.

In your browser (Options > Security), import the full public chain located here:
```sh
./pki/ca/full-ca-chain-public.pem
```

and test that the server authentication (TLS) is functionnal at [https://tls.localhost](https://tls.localhost).

**IMPORTANT**: remove this root CA at the end of your tests! If you keep it in your store, it is a huge security breach, as anyone can generate a valid certificate based on this root CA. You have been warned, **delete it** when you are done.

### Configure your browser for client auth
Now, it is time to test the client authentication for a full mTLS connexion.

In your browser (Options > Security), import one or all client certificates located at:
```sh
./pki/certs/alice.p12       (key=passwordalice)
./pki/certs/bob.p12         (key=passwordbob)
./pki/certs/charlie.p12     (key=passwordcharlie)
```
Each P12 file is protected by a key which need to be entered during import.

For tests, I recommand you to use the 'private navigation' mode to avoid cache and ease retries.

Test that the client authentication (mTLS) is functionnal at [https://mtls.localhost](https://mtls.localhost).

Note: if no client certificate are loaded, the mTLS fails and no HTTP code can be returned (even 403 or else) in this example.

### Going further
#### Header fields
As you have seen in the previous example, two fields are present in the HTTP header:
 - **X-Forwarded-Tls-Client-Cert**: contains the full x509 certificate
 - **X-Forwarded-Tls-Client-Cert-Info**: contains interpreted fields

You can use these fields with your backend for delivering specific content to the user depending of his identity and/or rights.

Test the parser with a very tiny app at [https://api.mtls.localhost](https://api.mtls.localhost). The example is based on FastAPI with python3.

#### Traefik configuration
By default in this example, Traefik will only allow Alice & Charlie (not Bob) as clients.

This is defined in:
```
./traefik_files/config/dyn/conf_dynamic.toml
```
You can either allow Bob, or allow all valid users with a certificate signed by the CA. Try it with the following content:
```
        caFiles = ["/pki/ca/signing-ca.crt"]
#       caFiles = [
#          "/pki/certs/alice.crt",
#          "/pki/certs/bob.crt",
#          "/pki/certs/charlie.crt"
#        ]
```
Please note: your browser will only display allowed certificates in the login choice during the connexion.

Also, take a look to all capabilities of mTLS in Traefik here: https://doc.traefik.io/traefik/https/tls/#client-authentication-mtls

#### Use a public CA
It is possible to use this template with a public CA (like Let's Encrypt) for server authentication. As far as I know, it will not be possible to have a public CA for client authentication because it does not exist.

To use Let's Encrypt, add a certresolver in your service, like this one:
```
- "traefik.http.routers.<service_name>.tls.certresolver=letsenc"
```
and uncomment the matching certresolver in `./traefik_files/config/traefik_static.yml`. That's all!

#### PKI management
For playing with the existing PKI of this repository, here is the password list used:
- root-ca: passwordca
- signing-ca: passwordsignca

# Clean your setup
**IMPORTANT**: remove the root CA at the end of your tests! If you keep it in your store, it is a huge security breach, as anyone can generate a valid certificate based on this root CA. You have been warned, **delete it** now.

