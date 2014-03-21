from __future__ import print_function

from lxml import etree

import gevent
from gevent import monkey
monkey.patch_all()

import requests
requests.adapters.DEFAULT_RETRIES = 1

import more_itertools
import argparse
import json


def retrieve_feeds(opml_data):
    root = etree.XML(opml_data)
    for feed in root.xpath("//outline[@type='rss']"):
        yield {'text': feed.attrib['text'], 'url': feed.attrib['xmlUrl']}


def retrieve_dead_feeds(feeds, chunked_size):
    session = requests.Session()

    def check_feed(feed):
        is_valid = False
        try:
            resp = session.get(feed['url'], allow_redirects=True, verify=False,
                               timeout=3)
            is_valid = (resp.status_code == 200)
        except:
            pass

        return (feed, is_valid)

    for chunked_feeds in more_itertools.chunked(feeds, chunked_size):
        jobs = [gevent.spawn(check_feed, feed) for feed in chunked_feeds]
        gevent.joinall(jobs)

        results = [job.value for job in jobs]
        for feed, is_valid in results:
            if not is_valid:
                yield feed


def output_dead_feeds(dead_feeds, progress=None):
    all_dead_feeds = []
    for dead_feed in dead_feeds:
        all_dead_feeds.append(dead_feed)
        if progress:
            progress(dead_feed)
    return all_dead_feeds


def output_progress(feed):
    print('bye, %s (%s)' % (feed['text'], feed['url']))


def main():
    parser = argparse.ArgumentParser(description='Check opml RSS links')
    parser.add_argument('filename', help='the opml file')

    parser.add_argument('--chunk-size', default=50, type=int,
                        help='request chunk size (default: %(default)d)')

    parser.add_argument('--silent', const=True, action='store_const',
                        help='no progess output')

    parser.add_argument('--output-json', type=argparse.FileType('w'),
                        default=None,
                        help='output json file')

    args = parser.parse_args()

    with open(args.filename) as f:
        data = f.read()
        feeds = retrieve_feeds(data)
        dead_feeds = retrieve_dead_feeds(feeds, args.chunk_size)

        progress_func = output_progress if not args.silent else None
        all_dead_feeds = output_dead_feeds(dead_feeds, progress_func)

        if args.output_json:
            data = json.dumps(all_dead_feeds,
                              indent=4, separators=(',', ': '))
            args.output_json.write(data)

if __name__ == '__main__':
    main()
