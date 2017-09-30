#!/usr/bin/env python3

"""
processData.py

A small helper script to aggregate the results of our LLDA usage
and write them into one JSON file which can be used for the
visualization.

    Copyright (c) 2017 Henning Gebhard
   
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
from os import path

DOC = "llda-cvb0-ce94edc0-31-16bf1ad8-1a4ce40b"
TID2TNAMES = {
    "0": "<empty>",
    "1": "Alltag",
    "2": "Angst",
    "3": "Auswanderung",
    "4": "Buchhandel",
    "5": "Drittes Reich",
    "6": "Film",
    "7": "Geld",
    "8": "Gesellschaftsordnung",
    "9": "Gesundheit",
    "10": "Hilfe",
    "11": "Judentum",
    "12": "Leid",
    "13": "Literatur",
    "14": "Nachkriegszeit",
    "15": "Ost-West-Konflikt",
    "16": "Post",
    "17": "Publizistik",
    "18": "Reise",
    "19": "Rezension",
    "20": "Textproduktion",
    "21": "Tod",
    "22": "Verfolgung",
    "23": "Verwaltung",
    "24": "Verwandschaft",
    "25": "Zensur",
    "26": "Zweiter Weltkrieg",
    "27": "Zwischenmenschliche Beziehungen",
    "481": "nonsense label '481'",
    "29": "nonsense label '29'",
    "26#": "WW2 (26 mit Leerstelle)"
}

###################################################################
# Der ganze mapping scheiß


def labelsToTopics():
    mapping = {}
    with open(path.join(DOC, "01000", "label-index.txt")) as f:
        for label, tid in enumerate(f):
            value = tid.replace("\xa0", "#").strip("\n")
            if not value:
                value = '0'
            mapping[str(label)] = value
    return mapping


def labelsToTopicNames():
    l2t = labelsToTopics()
    return {k: TID2TNAMES[v] for k, v in l2t.items()}


LDALABELS2TID = labelsToTopics()
LDALABELS2TNAMES = labelsToTopicNames()


###########################################################
# data extraction

def parse_gn_csv(input_file):
    """did, tids, filename, content -> did: {'filename': filename}"""
    index = {}
    with open(input_file, "r") as inf:
        for line in inf:
            parts = line.split(",")
            doc_id, title = parts[0], parts[2]
            index[doc_id] = {'filename': title, 'did': doc_id}
    return index


def parse_dtd_csv(input_file, documents):
    """documents is the parsed data from parse_gn_csv()
    did, label1, p1, label2, p2 [...]
    """
    with open(input_file, "r") as inf:
        for line in inf:
            parts = line.split(",")
            doc_id = parts[0]
            print("Document with ID %s" % doc_id)
            rest = parts[1:]
            rest = sorted(pairwise(rest), reverse=True, key=lambda tupel: tupel[1])
            topics = []
            offset = 0
            for label, p in rest:
                tid = LDALABELS2TID[label]
                tname = LDALABELS2TNAMES[label]
                if float(p) > 1:
                    p = 1
                if float(p) < 0:
                    p = 0
                topics.append({
                    'tid': tid,
                    'name': tname,
                    'p': float(p),
                    'offset': offset,
                })
                offset += float(p)
            documents[doc_id]["topics"] = topics
    return documents


def pairwise(iterable):
    """NOTE: this is unlike the pairwise recipe in python's
    itertools documentation. This implementation yields
    s -> (s0, s1), (s2, s3), (s4, s5)
    """
    a = iter(iterable)
    return zip(a, a)


def write_json(docs, filepath):
    d = []
    for doc_id, data in docs.items():
        d.append(data)
    with open(filepath, "w") as f:
        json.dump(d, f, indent=2)


def main():
    # Extract docID and doc filename
    documents = parse_gn_csv("./gn.csv")
    # Extract topics for each document
    documents = parse_dtd_csv(
        path.join(DOC, "document-topic-distributions.csv"),
        documents
    )
    write_json(documents, "data/documents.json")


if __name__ == '__main__':
    main()
