#!/usr/bin/env python2.7
import re

hits = {}
used = {}
impressionsPerAID = {}
spendPerAID = {}
clicksPerAID = {}
impressionsPerCID = {}
badRangeMessage = 'SCORE OUT OF RANGE'
noHitsMessage = 'NO HITS'
noImpressionsMessage = 'NO IMPRESSIONS'
noSpendsMessage = 'NO SPENDS'
noClicksMessage = 'NO CLICKS'

# Extract data from results summary.
def parse_summaries(summaries):
    for index, summary in enumerate(summaries):
		parse_summary(summary, index)

# Store summaries into dictionaries.
def parse_summary(summary,index):
	f = open(summary, 'r')
	lines = f.readlines()
	lineIndex = 0;
	while lineIndex < len(lines):
		line = lines[lineIndex]
		if 'Avg hits:' in line:
			hits[index] = int(line.split(':')[1])
		if 'Avg used:' in line:
			used[index] = int(line.split(':')[1])
		if 'Distribution of Impressions by Advertiser ID:' in line:
			impressionsPerAID[index] = parse_pairs(collect_pairs(lines,lineIndex))
			lineIndex += len(impressionsPerAID)
		if 'Distribution of Spend by Advertiser ID:' in line:
			spendPerAID[index] = parse_pairs(collect_pairs(lines,lineIndex))
			lineIndex += len(spendPerAID)
		if 'Distribution of Clicks by Advertiser ID:' in line:
			clicksPerAID[index] = parse_pairs(collect_pairs(lines,lineIndex))
			lineIndex += len(clicksPerAID)
		if 'Distribution of Impressions by Campaign ID:' in line:
			impressionsPerCID[index] = parse_pairs(collect_pairs(lines,lineIndex))
			lineIndex += len(impressionsPerCID)
		lineIndex += 1
	f.close()

def collect_pairs(lines,startIndex):
	pairs = []
	index = startIndex
	while True:
		index += 1
		pairs.append(lines[index])
		if "]" in lines[index]:
			break
	return pairs

def parse_pairs(pairs):
	dict = {}
	for pair in pairs:
		splitList = re.split(r'[(, )\']+', pair)
		key = splitList[1]
		valueString = splitList[2]
		if '.' in valueString:
			dict[key] = float(valueString)
		else:
			dict[key] = int(valueString)
	return dict
	
# Score for simulation statistics.
def compute_statistics_score():
	sumHitsUsed = sum(hits.itervalues())+sum(used.itervalues())
	absDiffs = 0.0 + abs(hits[0]-hits[1]) + abs(used[0]-used[1])
	if sumHitsUsed == 0:
		return noHitsMessage
	else:
		return (sumHitsUsed-absDiffs)/sumHitsUsed

# Extend each distribution with the ids of the other
def complement_distributions(dist):
	for id in dist[0].iterkeys():
		if id not in dist[1].iterkeys():
			dist[1][id] = 0
	for id in dist[1].iterkeys():
		if id not in dist[0].iterkeys():
			dist[0][id] = 0

# Score for distributions.
def compute_distribution_score(dist):
	complement_distributions(dist)
	sumTotalValues = sum(dist[0].itervalues())+sum(dist[1].itervalues())
	absDiffs = 0.0
	for id in dist[0].iterkeys():
		absDiffs += abs(dist[0][id]-dist[1][id])
	if sumTotalValues == 0:
		return noImpressionsMessage
	else:
		return (sumTotalValues-absDiffs)/sumTotalValues

def format_score(score):
	if score == noHitsMessage:
		return noHitsMessage
	if (score < 0.0) or (score > 1.0):
		return badRangeMessage
	return '{:>7.2%}'.format(score)

def print_stats(args):
	if len(args) != 3:
		print('Two filenames required as arguments')
	else:
		parse_summaries([args[1],args[2]])
		print('Similarity for simulation statistics:'+format_score((compute_statistics_score())))
		print('Similarity for impressions per advertiser id:'+format_score((compute_distribution_score(impressionsPerAID))))
		print('Similarity for spend per advertiser id:'+format_score((compute_distribution_score(spendPerAID))))
		print('Similarity for clicks per advertiser id:'+format_score((compute_distribution_score(clicksPerAID))))
		print('Similarity for impressions per campaign id:'+format_score((compute_distribution_score(impressionsPerCID))))

if __name__ == "__main__":
	import sys
	print_stats(sys.argv)