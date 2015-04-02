#!/usr/bin/env python2.7

import json
from pprint import pprint

#1st line in file may become summary data as per bug 6796001

def getMetrics(file):
    
    totalClicks=0
    tier1Clicks=0
    tier2Clicks=0
    tier3Clicks=0
    unclassifiedClicks=0
    totalEvents=0
    tier1Events=0
    tier2Events=0
    tier3Events=0
    unclassifiedEvents=0
    totalPaid=0.0
    tier1Paid=0.0
    tier2Paid=0.0
    tier3Paid=0.0
    unclassifiedPaid=0.0
    tier1sinpos1=0
    tier2sinpos1=0
    tier3sinpos1=0
    unclassifiedsinpos1=0
    noCreativesReturned=0
    
    totalAdvertisers=set()
    tier1Advsinpos1=set()
    tier2Advsinpos1=set()
    tier3Advsinpos1=set()
    unclassifiedAdvsinpos1=set()
    adClicks={}
    adImps={}
    
    #print 'filename is ' + file
    with open(file,'r') as simres:
        for line in simres:
            if line.startswith('#############'):
                break;
            totalEvents+=1
            result = json.loads(line)
            response = result['response'] #this is the bit withe creatives in it
            if len(response['creatives']) > 0: #in case no creaives were returned
                tier = response['creatives'][0]['advertiserTier']
                #print tier
                if tier=='TIER_1':
                    tier1sinpos1+=1
                    tier1Advsinpos1.add(response['creatives'][0]['advertiserId'])
                elif tier=='TIER_2':
                    tier2sinpos1+=1
                    tier2Advsinpos1.add(response['creatives'][0]['advertiserId'])
                elif tier=='TIER_3':
                    tier3sinpos1+=1
                    tier3Advsinpos1.add(response['creatives'][0]['advertiserId'])
                else:
                    unclassifiedsinpos1+=1
                    unclassifiedAdvsinpos1.add(response['creatives'][0]['advertiserId'])
            else:
                noCreativesReturned+=1
            for hits in response['creatives']:
                totalAdvertisers.add(hits['advertiserId'])
                totalClicks+=hits['clicks']
                totalPaid+=(hits['pricePaid']*hits['clicks'])#price paid is per click - 0 if no clicks,
                
                #advdertiser clicks/impressions
                if hits['advertiserId'] in adClicks:
                    adClicks[hits['advertiserId']]+=hits['clicks']
                else:
                    adClicks[hits['advertiserId']]=hits['clicks']
                if hits['advertiserId'] in adImps:
                    adImps[hits['advertiserId']]+=1
                else:
                    adImps[hits['advertiserId']]=1
                
                if hits['advertiserTier'] == 'TIER_1':
                    tier1Events+=1
                    tier1Clicks+=hits['clicks']
                    tier1Paid+=(hits['pricePaid']*hits['clicks'])
                elif hits['advertiserTier'] == 'TIER_2':
                    tier2Events+=1
                    tier2Clicks+=hits['clicks']
                    tier2Paid+=(hits['pricePaid']*hits['clicks'])
                elif hits['advertiserTier'] == 'TIER_3':
                    tier3Events+=1
                    tier3Clicks+=hits['clicks']
                    tier3Paid+=(hits['pricePaid']*hits['clicks'])
                else:
                    unclassifiedEvents+=1
                    unclassifiedClicks+=hits['clicks']
                    unclassifiedPaid+=(hits['pricePaid']*hits['clicks'])
    
    tier1CTR=0.0
    tier1CPC=0.0
    tier1CPM=0.0
    if tier1Events > 0:
        tier1CTR=float(tier1Clicks)/float(tier1Events)
        tier1CPM=1000.0*tier1Paid/tier1Events
        if tier1Clicks > 0:
            tier1CPC=tier1Paid/tier1Clicks

    tier2CTR=0.0
    tier2CPM=0.0
    tier2CPC=0.0
    if tier2Events > 0:
        tier2CTR=float(tier2Clicks)/float(tier2Events)
        tier2CPM=1000.0*tier2Paid/tier2Events
        if tier2Clicks > 0:
            tier2CPC=tier2Paid/tier2Clicks


    tier3CTR=0.0
    tier3CPM=0.0
    tier3CPC=0.0
    if tier3Events > 0:
        tier3CTR=float(tier3Clicks)/float(tier3Events)
        tier3CPM=1000.0*tier3Paid/tier3Events
        if tier3Clicks > 0:
            tier3CPC=tier3Paid/tier3Clicks

    unclassifiedCTR=0.0
    unclassifiedCPC=0.0
    unclassifiedCPM=0.0
    if unclassifiedEvents > 0:
        unclassifiedCTR=float(unclassifiedClicks)/float(unclassifiedEvents)
        unclassifiedCPM=1000.0*unclassifiedPaid/unclassifiedEvents
        if unclassifiedClicks > 0:
            unclassifiedCPC=unclassifiedPaid/unclassifiedClicks


    globalCPC=0.0;
    globalCTR=float(totalClicks)/float(totalEvents)
    if totalClicks > 0:
        globalCPC=totalPaid/totalClicks
    globalCPM=1000.0*totalPaid/totalEvents

    #winners and losers
    from operator import itemgetter #for sorting dict by value
    sortedAdClicks=sorted(adClicks.iteritems(), key=itemgetter(1),reverse=True)
    sortedAdImps=sorted(adImps.iteritems(),key=itemgetter(1),reverse=True)

    toShow=10;
    if len(sortedAdClicks) < 10:
        toShow=len(sortedAdClicks)

    # gini coefficient calculated as per 2nd equation (since dat is sorted) of http://mathworld.wolfram.com/GiniCoefficient.html

    i=0
    giniClicks=1
    giniImps=0
    totImps=0
    n=len(sortedAdClicks)
    for adClicks in list(reversed(sortedAdClicks)): #list initially reverse sorted!
        i+=1
        giniClicks+=(2*i-n-1)*adClicks[1] #adClicks is tuple with advertiserId [0] and clicks [1] in
        #print adClicks[1]
        #print str(i)
    #print 'Total clicks: ' + str(totalClicks)
    clickMu=float(totalClicks)/float(n)
    #giniClicks=float(giniClicks)/float(n*n*clickMu)


    i=0
    for adImps in list(reversed(sortedAdImps)): #list is initially reverse sorted!
        i+=1
        totImps+=adImps[1]
        giniImps+=(2*i-n-1)*adImps[1] #adClicks is tuple with advertiserId [0] and clicks [1] in
        #print adImps[1]
        #print str(i)
    #print 'Total impressions: ' + str(totImps)
    impsMu=float(totImps)/float(n)
    #giniImps=float(giniImps)/float(n*n*impsMu)



    print '********Overall Summary********'

    print 'There were ' + str(noCreativesReturned) + ' (' + str(100.0*float(noCreativesReturned)/float(totalEvents)) + '%) events where no creatives were returned! (out of ' + str(totalEvents) + ')\n'

                                               
    print str(len(totalAdvertisers)) + ' advertisers participated and won *a place* (not necessarily first place) in auctions\n'
    
    print 'Total revenue was ' + str(totalPaid) + '\n'
    
    print 'Global CTR was ' + str(globalCTR) + ' (' + str(totalClicks) + '/' + str(totalEvents) + ')'
    print 'Global CPC was ' + str(globalCPC) + ' (' + str(totalPaid) + '/' + str(totalClicks) + ')'
    print 'Global CPM was ' + str(globalCPM) + ' (1000 x ' + str(totalPaid) + '/' + str(totalEvents) + ')'
    Gclicks=0.0 #protect against case where there are no clicsk at all (no-one gets any clicks = everyone gets zero clicks
    if clickMu > 0:
        Gclicks = float(giniClicks)/float(n*n*clickMu)
    print 'Gini coefficient (clicks) is ' + str(Gclicks) + ' (' + str(float(giniClicks)) + '/(' + str(float(n)) + ' * ' + str(float(n)) + ' * ' + str(clickMu) + ')'
    print 'Gini coefficient (impressions) is ' + str(float(giniImps)/float(n*n*impsMu)) + ' (' + str(float(giniImps)) + '/(' + str(float(n)) + ' * ' + str(float(n)) + ' * ' + str(impsMu) + ')\n'


    print '********Tiering Summary********'

    print str(float(tier1sinpos1)/float(totalEvents)*100.0) + '% (' + str(tier1sinpos1) + '/' + str(totalEvents) + ') tier1 creatives were in position 1 (from ' + str(len(tier1Advsinpos1)) + ' advertisers)'
    print str(float(tier2sinpos1)/float(totalEvents)*100.0) + '% (' + str(tier2sinpos1) + '/' + str(totalEvents) + ') tier2 advertisers were in position 1 (from ' + str(len(tier2Advsinpos1)) + ' advertisers)'
    print str(float(tier3sinpos1)/float(totalEvents)*100.0) + '% (' + str(tier3sinpos1) + '/' + str(totalEvents) + ') tier3 advertisers were in position 1 (from ' + str(len(tier3Advsinpos1)) + ' advertisers)'
    print str(float(unclassifiedsinpos1)/float(totalEvents)*100.0) + '% (' + str(unclassifiedsinpos1) + '/' + str(totalEvents) + ') unclassified tier advertisers were in position 1 (from ' + str(len(unclassifiedAdvsinpos1)) + ' advertisers)\n'

    print '\n********Tier 1********'

    print 'Total revenue from Tier 1 advertisers was ' + str(tier1Paid)
    print 'Tier 1 CTR was ' + str(tier1CTR)
    print 'Tier 1 CPC was ' + str(tier1CPM)
    print 'Tier 1 CPM was ' + str(tier1CPM) + '\n'

    print '\n********Tier 2********'

    print 'Total revenue from Tier 2 advertisers was ' + str(tier2Paid)
    print 'Tier 2 CTR was ' + str(tier2CTR)
    print 'Tier 2 CPC was ' + str(tier2CPM)
    print 'Tier 2 CPM was ' + str(tier2CPM) + '\n'

    print '\n********Tier 3********'

    print 'Total revenue from Tier 3 advertisers was ' + str(tier3Paid)
    print 'Tier 3 CTR was ' + str(tier3CTR)
    print 'Tier 3 CPC was ' + str(tier3CPM)
    print 'Tier 3 CPM was ' + str(tier3CPM) + '\n'

    print '\n********Tier Unclassified********'
    
    print 'Total revenue from Tier Unclassified advertisers was ' + str(unclassifiedPaid)
    print 'Tier Unclassified CTR was ' + str(unclassifiedCTR)
    print 'Tier Unclassified CPC was ' + str(unclassifiedCPM)
    print 'Tier Unclassified CPM was ' + str(unclassifiedCPM) + '\n'

    print '********Winners********\nThe following advertisers got the most clicks (max. top 10):'
    pprint(sortedAdClicks[0:toShow])

    print '\nThe following advertisers got the most impressions (max. top 10):'
    pprint(sortedAdImps[0:toShow])

    print '\n********Losers********\nThe following advertisers got the least clicks (max. lowest10)'
    pprint(sortedAdClicks[-toShow:])

    print '\n********Losers********\nThe following advertisers got the least impressions (max. lowest10)'
    pprint(sortedAdImps[-toShow:])






if __name__ == "__main__":
    import sys
    getMetrics(sys.argv[1])


