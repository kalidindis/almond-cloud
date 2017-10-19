#!/usr/bin/python3

import os, sys, csv
import shutil

from Naked.toolshed.shell import execute_js 
from turk_scrubber import scrubber

SENTENCES_PER_HIT = 3
PARAPHRASE_PER_SENTENCE = 3

def format(inp_format, path):
    """ format raw turk data to: 'id, tt/target_json, sentence, paraphrase'
    """
    with open(os.path.join(path, 'raw.csv'), 'r') as fin, open(os.path.join(path, 'data.csv'), 'w') as fout:
        reader = csv.reader(fin, delimiter=',', quotechar='\"')
        writer = csv.writer(fout, delimiter=',', quotechar='\"')

        headers = next(reader)
        idx_rejection = headers.index('RejectionTime')
        idx_info = headers.index('Input.id1')
        idx_paraphrase = headers.index('Answer.Paraphrase1-1')
        
        for row in reader:
            # skip rejected answer
            if (row[idx_rejection] != ''):
                continue
            for i in range(SENTENCES_PER_HIT):
                ttid = row[idx_info + i*3]
                if inp_format == 'tt':
                    tt = row[idx_info + i*3 + 1]
                else:
                    target_json = row[idx_info + i*3 + 1]
                sentence = row[idx_info + i*3 + 2].lower()
                for j in range(PARAPHRASE_PER_SENTENCE):
                    idx = idx_paraphrase + i*PARAPHRASE_PER_SENTENCE + j
                    paraphrase = row[idx].replace('\n', ' ').lower()
                    if inp_format == 'tt':
                        writer.writerow([ttid, tt, sentence, paraphrase])
                    else:
                        writer.writerow([ttid, target_json, sentence, paraphrase])


def tt_to_sempre(inp_format, rule_type, path):
    """ run js script to get sempre json and parameter count
    """
    script = './turk_to_sempre.js'
    execute_js(script, ' '.join([inp_format, rule_type, path]))


def clean(rule_type, path):
    """ clean data
    """
    with open(os.path.join(path, 'data-sempre.csv'), 'r') as data, \
         open(os.path.join(path, 'cleaned.csv'), 'w') as cleaned, \
         open(os.path.join(path, 'dropped.csv'), 'w') as dropped:
        reader = csv.reader(data, delimiter=',', quotechar='\"')
        writer_cleaned = csv.writer(cleaned, delimiter=',', quotechar='\"')
        writer_dropped = csv.writer(dropped, delimiter=',', quotechar='\"')
        for row in reader:
            scrubbed, row = scrubber(rule_type, row)
            if scrubbed:
                writer_cleaned.writerow(row)
            else:
                writer_dropped.writerow(row)


def main():
    # argv[1] = 'tt' or 'json'
    inp_format = sys.argv[1]
    assert (inp_format == 'tt' or inp_format == 'json'), "wrong input format: %s" % inp_format
    rule_type = sys.argv[2]
    assert (rule_type == 'permission' or rule_type == 'command'), "wrong rule type: %s" % inp_format
    path = os.path.join(sys.argv[3])
    if len(sys.argv) > 4:
       global PARAPHRASE_PER_SENTENCE
       PARAPHRASE_PER_SENTENCE = int(sys.argv[4])

    format(inp_format, path)
    tt_to_sempre(inp_format, rule_type, path)
    clean(rule_type, path)


main()
