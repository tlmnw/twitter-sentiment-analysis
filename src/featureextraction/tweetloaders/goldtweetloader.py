#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import tweetloader
import os
import csv
import codecs
from extractors.statsextractor import DefiniteSentimentExtractor as sent
import hashlib
import socket
import json
from StringIO import StringIO

class GoldTweet(object):

    def __init__(self,tweetID):
        self.tweetID = tweetID
        self.tweet = None

    def __str__(self):
        return "%s: %s" % (self.tweetID, self.tweet)

def _getDaiAnnotation(token):
    #"positive", "negative", "neutral" or "na" (for irrelevant/unclear).    
    if token == "positive":
        return sent.POS
    elif token == "negative":
        return sent.NEG
    elif token == "neutral":    
        return sent.NEU
    elif token == "na":
        return None
    else:
        raise ValueError("Unknown annotation: %s" % token)


def loadDaiTweets(csvFile):
    fh = open(csvFile, "r")
    reader = csv.reader(fh, delimiter='\t'.encode('utf-8'))
    # skip header
    reader.next()
    for row in reader:
        #sentiment numberagreed tweetid tweet
        t = GoldTweet(row[2].decode("utf-8"))
        t.tweet = row[3].decode("utf-8")
        se = row[0].decode("utf-8")
        getRemoteStats(t)
        t.goldStats = { "sentiment" : _getDaiAnnotation(se), "numberagreed" : int(row[1]) }
        yield t
    fh.close() 

def _getCuiAnnotation(token):
    if token == "&":
        # not sure
        return None
    elif token == "+":
        return sent.POS
    elif token == "-":
        return sent.NEG
    elif token == "0":
        return sent.NEU
    else:
        raise ValueError("Unknown annotation: %s" % token)

def loadCuiTweets(csvFile, annotationsFile, lang="de"):
    fh = open(annotationsFile)
    reader = csv.reader(fh, delimiter="\t".encode("utf-8"))
    sentiment = []
    numberagreed = []
    for row in reader:
        if row[0].decode("utf-8").startswith("#"):
            # is comment
            continue
        sentiment.append(_getCuiAnnotation(row[0].decode("utf-8")))
        na = row[1].decode("utf-8")[0]
        numberagreed.append(int(na))
    fh.close()
    fh = open(csvFile)
    reader = csv.reader(fh, delimiter="\t".encode("utf-8"))
    count = 0
    for row in reader:
        # 6       205     en      0.73906744      2009-06-11 Tweet TweetEN
        l = row[2].decode("utf-8").strip()
        if l == lang:
            se = sentiment[count]
            if se is None:
                # "not sure"
                continue
            date = row[4].decode("utf-8")
            tweet = row[5].decode("utf-8")
            t = GoldTweet(hashlib.md5((tweet + date).encode("utf-8")).hexdigest())
            t.tweet = tweet
            getRemoteStats(t)
            t.goldStats = {"sentiment" : sentiment[count],
                "numberagreed": numberagreed[count]}
            yield t
        count += 1

def getRemoteStats(tweetObj):
    #my $remote_host="localhost";
    #my $remote_port="1234";

    #my $socket = IO::Socket::INET->new("$remote_host:$remote_port");

    #print $socket "OMG!!!! :-)  Hallo Welt!! Schlecht!\n";
    #my $line = <$socket>;
    #print $line."\n";
    #create an INET, STREAMing socket
    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    #now connect to the web server on port 80
    # - the normal http port
    s.connect(("localhost", 1234))
    fh = s.makefile()
    assert type(tweetObj.tweet) == unicode
    fh.write(tweetObj.tweet.encode("utf-8"))
    fh.write("\n\n")
    fh.flush()
    l = fh.readline().decode("utf-8")
    stats = json.loads(l)
    print stats
    tweetObj.stats = stats
    statsFH = StringIO("".join(stats["tweet"]).encode("utf-8"))
    tweetloader.loadTweetSentiment(tweetObj, fh=statsFH)
    del stats["tweet"]
    return tweetObj

    



