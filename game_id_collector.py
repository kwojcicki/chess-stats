import requests
from bs4 import BeautifulSoup
import json
import sys
import getopt
import time


def get_games(low: int, high: int, page: int):
    url = 'https://lichess.org/games/search?ratingMin=' + str(low) + '&ratingMax=' + str(high) + \
          '&sort.field=d&sort.order=desc&perf=2&analysed=1#results'

    if page > 0:
        url = 'https://lichess.org/games/search?page=' + str(page) +\
              '&ratingMin=' + str(low) + '&ratingMax=' + str(high) + \
              '&sort.field=d&sort.order=desc&perf=2&analysed=1'

    html_text = requests.get(url).text
    # print(html_text)
    soup = BeautifulSoup(html_text, 'html.parser')
    # print(soup)

    games = soup.findAll("a", {"class": "game-row__overlay"})

    #print(games)
    #for game in games:
        #print(game['href'])

    def get_id(x):
        return x['href'].split("/")[1]

    return list(map(get_id, games))


def main(argv):
    low = 600
    high = 2900
    games = 30
    try:
        opts, args = getopt.getopt(argv, "l:h:n:")
    except getopt.GetoptError:
        # print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in "-l":
            low = arg
        elif opt in "-h":
            high = arg
        elif opt in "-n":
            games = int(arg)

    print(low, high, games)

    curr = int(low)
    while curr < high:
        print("Getting", games, "games between the ranking of", curr, "to", curr + 100)

        game_ids = []
        page = 0
        while len(game_ids) < games:
            print("Getting page", page)
            for game in get_games(curr, curr + 100, page):
                game_ids.append(game)
            page += 1

        print(json.dumps(game_ids, indent=4, sort_keys=True, default=str))

        with open(str(curr) + '-' + str(curr + 100) + '-' + str(games) + '.txt', 'w') as outfile:
            json.dump(game_ids, outfile, default=str)

        time.sleep(120)
        curr += 100


if __name__ == "__main__":
    main(sys.argv[1:])
