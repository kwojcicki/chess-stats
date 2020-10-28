import matplotlib.pyplot as plt
import numpy as np
import berserk
import json
import glob
import time
from operator import add

bucket_size = 20
buckets = [[] for _ in range(int(3500 / bucket_size))]


def get_data(games):
    # acpl: average centipawn loss
    with open('./token.txt') as f:
        token = f.read()
        session = berserk.TokenSession(token)
        client = berserk.Client()

        # for game in games:
        game_results = client.games.export_multi(*games, evals="true", moves="true")

        for game_result in game_results:
            # print(game_result)
            # print(json.dumps(game_result, indent=4, sort_keys=True, default=str))
            # print(game_result["players"]["black"]["analysis"])
            # avg_elo = (game_result["players"]["black"]["rating"] + game_result["players"]["white"]["rating"])/2
            # print(avg_elo)
            # buckets[int(avg_elo / bucket_size)].append(game_result["players"]["black"]["analysis"]['blunder'])
            if "aiLevel" not in game_result["players"]["black"]:
                buckets[int(game_result["players"]["black"]["rating"] / bucket_size)].\
                    append(game_result["players"]["black"]["analysis"])

            if "aiLevel" not in game_result["players"]["white"]:
                buckets[int(game_result["players"]["white"]["rating"] / bucket_size)]. \
                    append(game_result["players"]["white"]["analysis"])


def main():
    ids = glob.glob('[0-9]*-[0-9]*-[0-9]*.txt')
    # ids = glob.glob('600-700-100.txt')
    for file in ids:
        with open(file) as json_file:
            print(file)
            get_data(json.load(json_file))
            time.sleep(10)


main()

with plt.xkcd():
    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    # ax.set_xticks([])
    # ax.set_yticks([])
    # ax.set_ylim([-30, 10])

    def get_acpl(x):
        return x["acpl"]


    def get_second(x):
        return x[1]

    modified = [list(map(get_acpl, x)) for x in buckets]
    xs = list()
    ys = list()
    i = 0
    for x in modified:
        if len(x) > 0:
            xs.append(i)
            ys.append(sum(x) / len(x))
        i += 1

    ax.plot(xs, ys)

    ax.set_xlabel('Rating')
    ax.set_ylabel('ACPL')

    plt.yticks(np.arange(0, max(ys) + 2, 20))
    plt.xticks(np.arange(0, len(buckets), 1 * 35), np.arange(0, 3500, bucket_size * 35))

    ax.set_xlim([25, len(buckets)])

plt.show()

with plt.xkcd():
    # blunder
    # ': 1,
    # 'inaccuracy': 4,
    # 'mistake

    def get_mistakes(x):
        return x["mistake"]

    def get_blunders(x):
        return x["blunder"]

    def get_inaccuracies(x):
        return x["inaccuracy"]

    all_ys = list()
    for get_x in [get_mistakes, get_blunders, get_inaccuracies]:
        modified = [list(map(get_x, x)) for x in buckets]
        xs = list()
        ys = list()
        i = 0
        for x in modified:
            if len(x) > 0:
                xs.append(i)
                ys.append(sum(x) / len(x))
            i += 1
        all_ys.append(ys)

    y = np.row_stack((all_ys[0], all_ys[1], all_ys[2]))

    x = xs
    y_stack = np.cumsum(y, axis=0)  # a 3x10 array

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.fill_between(x, 0, y_stack[0, :], facecolor="#CC6666", alpha=.7, label="Mistakes")
    ax1.fill_between(x, y_stack[0, :], y_stack[1, :], facecolor="#1DACD6", alpha=.7, label="Blunders")
    ax1.fill_between(x, y_stack[1, :], y_stack[2, :], facecolor="#6E5160", label="Inaccuracies")

    ax1.set_xlabel('Rating')
    ax1.set_ylabel('Errors')
    plt.xticks(np.arange(0, len(buckets), 1 * 35), np.arange(0, 3500, bucket_size * 35))
    # ax1.set_ylim([0, max((max(all_ys[0]), max(all_ys[1]), max(all_ys[2]))) + 2])

    plt.yticks(np.arange(0, max(list(map(add, list(map(add, all_ys[0], all_ys[1])), all_ys[2]))) + 3, 2))

    # plt.legend(loc='lower right')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
               ncol=3, fancybox=True, shadow=True)

plt.show()
