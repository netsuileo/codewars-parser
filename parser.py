from grab import Grab
import urllib
import argparse
import getpass
import json
import logging


def parse_arguments():
    parser = argparse.ArgumentParser(description='Parser for fetching katas from codewars.com')
    parser.add_argument('--email', type=str, help='User email', required=True)
    args = parser.parse_args()
    return args.email


def login(g, email, password):
    g.go('https://www.codewars.com/users/sign_in')
    g.doc.set_input('user[email]', email)
    g.doc.set_input('user[password]', password)
    g.doc.submit()


def main():
    email = parse_arguments()
    password = getpass.getpass()

    g = Grab()

    # Authenticating
    logging.info("Trying to authenticate")
    login(g, email, password)
    if not g.doc.url.endswith('dashboard'):
        logging.error("Authentication failed")
        return

    # Getting katas
    ids = []
    g.go('http://www.codewars.com/kata/search/python?q=&beta=false&page=1')
    katas = []
    for kata_info in g.doc.select("//div[@class='info-row']"):
        id = kata_info.attr('data-id')
        with urllib.request.urlopen('https://www.codewars.com/api/v1/code-challenges/{0}'.format(id)) as r:
            kata_json = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            print('kata {0} has been fetched'.format(id))
            katas.append(kata_json)

    print(katas)


if __name__ == '__main__':
    main()
