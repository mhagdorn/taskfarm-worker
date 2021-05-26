#!/bin/env python

import argparse
import pandas
import matplotlib
from matplotlib import pyplot

fields = ['total', 'getTask', 'updateTask', 'doneTask']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='+', help="csv files to read")
    parser.add_argument('-t', '--type', choices=fields, default='total',
                        help="select which field to plot")
    parser.add_argument('-o', '--output', help="save figure")
    args = parser.parse_args()

    matplotlib.style.use('ggplot')

    data = []
    for f in args.input:
        data.append(pandas.read_csv(f))

    data = pandas.concat(data, ignore_index=True, sort=False)
    data = data.astype({'nClients': int, 'nWorkers': int})

    selected_data = data.groupby(['nClients', 'nWorkers'])[args.type]
    selected_data.sum().unstack().plot.bar()
    pyplot.title(args.type)
    pyplot.ylabel('mean time [s]')
    pyplot.xlabel('number of clients')

    if args.output is not None:
        pyplot.savefig(args.output)
    else:
        pyplot.show()


if __name__ == '__main__':
    main()
