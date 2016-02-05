from grab import Grab
import urllib
import argparse
import getpass
import json
from math import ceil


PAGE_SIZE = 30

def parse_arguments():
    parser = argparse.ArgumentParser(description='Parser for fetching katas from codewars.com')
    parser.add_argument('--email', type=str, help='User email', required=True)
    parser.add_argument('--output', type=str, help='Output filename', required=True)
    parser.add_argument('--pages', nargs='+', type=int, help='Pages that need to be fetched. ex. 0 1 2', required=False)
    args = parser.parse_args()
    return args


def login(g, email, password):
    g.go('https://www.codewars.com/users/sign_in')
    g.doc.set_input('user[email]', email)
    g.doc.set_input('user[password]', password)
    g.doc.submit()


def main():
    args = parse_arguments()
    email = args.email
    password = getpass.getpass()
    output_filename = args.output

    g = Grab()

    # Authenticating
    print("Trying to authenticate")
    login(g, email, password)
    if not g.doc.url.endswith('dashboard'):
        print("Authentication failed")
        return
    print("Authentication succeed")

    # Getting pages amount
    if args.pages:
        pages = args.pages
    else:
        g.go('http://www.codewars.com/kata/search/python?q=&beta=false&page=0')
        # parsing node <p class='mlx mtn is-gray-text'>"710 Kata Found"</p>
        katas_amount = int(g.doc.select("//p[@class='mlx mtn is-gray-text']")[0].text().split()[0])
        pages = list(range(0, ceil(katas_amount/PAGE_SIZE)))

    # Getting katas ids
    print("Fetching katas ids'")
    katas_ids = []
    for page_num in pages:
        print("Getting ids from page {0}".format(page_num))
        g.go('http://www.codewars.com/kata/search/python?q=&beta=false&page={0}'.format(page_num))
        katas_infos = g.doc.select("//div[@class='info-row']")
        katas_ids.extend(map(lambda x: x.attr('data-id'), katas_infos))
    print("{0} katas at all".format(len(katas_ids)))

    # Getting katas
    katas = []
    for i, kata_id in enumerate(katas_ids, start=1):
        with urllib.request.urlopen('https://www.codewars.com/api/v1/code-challenges/{0}'.format(kata_id)) as r:
            kata_json = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            print('Kata {0} with id {1} has been fetched'.format(i, kata_id))
            katas.append(kata_json)

    # Writing to output
    output = open(output_filename, 'w')
    output.write(json.dumps({'katas': katas}, indent=4))
    output.close()


if __name__ == '__main__':
    main()
