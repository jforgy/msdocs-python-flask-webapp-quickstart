import os
import requests
import json
from datetime import datetime
import pygsheets
import pandas as pd
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, make_response)

app = Flask(__name__)


@app.route('/')
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    bankroll = request.cookies.get('Bankroll')
    kelly = request.cookies.get('KellyMultiplier')
    if bankroll is None:
        bankroll = '1000'
    if kelly is None:
        kelly = '.25'
    games = getData(bankroll, kelly)
    resp = make_response(render_template(
        'index.html',
        title='Home Page',
        tables =[games.to_html(index=False, classes='table table-striped" id="bets')],
        titles = games.columns.values,
        year=datetime.now().year,
        bankroll = bankroll,
        kelly = kelly,
    ))
    resp.set_cookie('Bankroll', bankroll, max_age=99999999)
    resp.set_cookie('KellyMultiplier', kelly, max_age=99999999)
    return resp


@app.route('/pitcherprops')
def pitcherprops():
    """Renders the home page."""
    bankroll = request.cookies.get('Bankroll')
    kelly = request.cookies.get('KellyMultiplier')
    if bankroll is None:
        bankroll = '1000'
    if kelly is None:
        kelly = '.25'

    games = getPitcherProps()
    resp = make_response(render_template(
        'PitcherProps.html',
        title='Home Page',
        games = games,
        year=datetime.now().year,
        bankroll = bankroll,
        kelly = kelly
    ))
    resp.set_cookie('Bankroll', bankroll, max_age=99999999)
    resp.set_cookie('KellyMultiplier', kelly, max_age=99999999)
    return resp

@app.route('/h2hpitchers')
def h2hpitchers():
    """Renders the home page."""
    bankroll = request.cookies.get('Bankroll')
    kelly = request.cookies.get('KellyMultiplier')
    if bankroll is None:
        bankroll = '1000'
    if kelly is None:
        kelly = '.25'

    games = getPitcherH2H()
    resp = make_response(render_template(
        'H2HPitchers.html',
        title='H2H Pitchers',
        games = games,
        year=datetime.now().year,
        bankroll = bankroll,
        kelly = kelly
    ))
    resp.set_cookie('Bankroll', bankroll, max_age=99999999)
    resp.set_cookie('KellyMultiplier', kelly, max_age=99999999)
    return resp

@app.route('/czrvsfd')
def czrvsfdks():
    """Renders the home page."""
    bankroll = request.cookies.get('Bankroll')
    kelly = request.cookies.get('KellyMultiplier')
    if bankroll is None:
        bankroll = '1000'
    if kelly is None:
        kelly = '.25'

    games = CZRvsFD()
    resp = make_response(render_template(
        'czrvsfd.html',
        title='CZR vs FD',
        games = games,
        year=datetime.now().year,
        bankroll = bankroll,
        kelly = kelly
    ))
    resp.set_cookie('Bankroll', bankroll, max_age=99999999)
    resp.set_cookie('KellyMultiplier', kelly, max_age=99999999)
    return resp

@app.route('/data')
def data():
    data = CZRvsFD()
    response = app.response_class(
        response = json.dumps(data),
        status = 200,
        mimetype='application/json'
        )
    return response


def getData(bankroll, kelly):
    """Renders the contact page."""
    gc = pygsheets.authorize(service_file='./creds.json')
    sh = gc.open('Pitcher Duels')
    wks = sh[0]                      
    games = wks.get_as_df()
    if not game.empty:
      games['BetSize'] = games['BetSize'].apply(lambda x: int(bankroll) * .01 * float(kelly) * x)
      games['BetSize'] = games['BetSize'].apply('${:,.2f}'.format)    
      games['Bet_Name'] = games['Bet_Name'].str.split().str[-2:].str.join(' ')

    print(games)
    return games

def getPitcherProps():
    games = list()
    fd_all_url = "https://sbapi.il.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FChicago"
    mgm_all_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixtures?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&fixtureTypes=Standard&state=Latest&offerMapping=MainMarkets&sortBy=FixtureStage&competitionIds=75&virtualCompetitionIds="
    #mgm_all_url = "https://api.americanwagering.com/regions/us/locations/il/brands/czr/sb/v3/sports/football/events/schedule"
    mgm_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    fd_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'cache-control': 'no-cache',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
        }
    mgm_all = requests.get(mgm_all_url, headers = mgm_headers)
    mgm_all = mgm_all.json()
    fd_all = requests.get(fd_all_url, headers = fd_headers)
    fd_all = fd_all.json()
    for i in mgm_all["fixtures"]:
        id = i["id"]
        if len(i["participants"]) > 0:
            #print(i["startDate"])
            #2023-07-25T22:40:00Z
            mgmGameStart = datetime.strptime(i["startDate"], '%Y-%m-%dT%H:%M:%SZ')
            away = i["participants"][0]["name"]["short"]
            for fd in fd_all["attachments"]["events"]:
                fdGameStart = datetime.strptime(fd_all["attachments"]["events"][fd]["openDate"], '%Y-%m-%dT%H:%M:%S.%fZ')
                if (away in fd_all["attachments"]["events"][fd]["name"]) and (mgmGameStart.day == fdGameStart.day) and (mgmGameStart.hour == fdGameStart.hour):
                    #print("FD: {}".format(fd_all["attachments"]["events"][fd]["openDate"]))
                    #print(away)
                    #create game, may be scrapped later if no lines are added
                    #print(fd_all["attachments"]["events"][fd]["name"])
                    fd_one_id = fd_all["attachments"]["events"][fd]["eventId"]
                    #break
            fd_one_url = "https://sbapi.il.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={}&tab=pitcher-props".format(fd_one_id)
            fd = requests.get(fd_one_url, headers = fd_headers)
            fd=fd.json()        
            fd = fd["attachments"]["markets"]
            data =[]            
            for i in fd:
                if "Alt Strikeouts" in fd[i]["marketName"]:
                    data.append(fd[i])
        mgm_one_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixture-view?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&offerMapping=All&scoreboardMode=Full&fixtureIds={}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false&useRegionalisedConfiguration=true".format(id)
        mgm = requests.get(mgm_one_url, headers = mgm_headers)
        mgm=mgm.json()
        for i in mgm["fixture"]["games"]:
            if len(data) == 2:
                game = {"Name": mgm["fixture"]["name"]["value"], "Lines": list(), "AwayPitcher": "", "HomePitcher": ""}                                             
                awayPitcher = data[0]["marketName"].split("-")[0]
                homePitcher = data[1]["marketName"].split("-")[0]
                game["awayPitcher"] = awayPitcher
                game["homePitcher"] = homePitcher
                if "Starting Pitcher Props" in i["name"]["value"] and awayPitcher in i["name"]["value"]:
                    print(i["name"]["value"])
                    for p in i["results"]:
                        if "Strikeouts" in p["name"]["value"]:
                            print("MGM - {}: {}".format(p["name"]["value"], p["americanOdds"]))
                            str = "{}{}+".format(awayPitcher, p["attr"])
                            for r in data[0]["runners"]:
                                #rint(r)
                                #print(str)
                                name = r["runnerName"]
                                #print(r["runnerName"])
                                if str in name:
                                    devigurl = "https://api.crazyninjaodds.com/api/devigger/v1/sportsbook_devigger.aspx?api=open&legodds={}/7%&finalodds={}&devigmethod=4&args=ev_p,kelly".format(r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], p["americanOdds"])
                                    devig = requests.get(devigurl)
                                    devig = devig.json()
                                    print("FD - {}: {}".format(r["runnerName"], r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"]))
                                    DevigLink = "http://crazyninjamike.com/Public/sportsbooks/sportsbook_devigger.aspx?autofill=1&LegOdds={}%2f7%25&FinalOdds={}".format(r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], p["americanOdds"])
                                    if "Final" in devig:
                                        fullKelly = devig["Final"]["Kelly_Full"]
                                        bankroll = request.cookies.get('Bankroll')
                                        kelly = request.cookies.get('KellyMultiplier')
                                        if bankroll is None:
                                            bankroll = 1000
                                        if kelly is None:
                                            kelly = .25

                                        betSize = int(bankroll) * .01 * float(kelly) * fullKelly
                                        Line = {"Name": name, "FanduelOdds": r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], "MGMOdds": p["americanOdds"], "EVPercentage": '{:.2%}'.format(devig["Final"]["EV_Percentage"]), "BetSize": '${:,.2f}'.format(betSize), "DevigLink": DevigLink}
                                        game["Lines"].append(Line)
                if "Starting Pitcher Props" in i["name"]["value"] and homePitcher in i["name"]["value"]:
                    print(i["name"]["value"])
                    for p in i["results"]:
                        if "Strikeouts" in p["name"]["value"]:
                            print("MGM - {}: {}".format(p["name"]["value"], p["americanOdds"]))
                            str = "{}{}+".format(homePitcher, p["attr"])
                            for r in data[1]["runners"]:
                                #rint(r)
                                #print(str)
                                name = r["runnerName"]
                                #print(r["runnerName"])
                                if str in name:
                                    devigurl = "https://api.crazyninjaodds.com/api/devigger/v1/sportsbook_devigger.aspx?api=open&legodds={}/7%&finalodds={}&devigmethod=4&args=ev_p,kelly".format(r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], p["americanOdds"])
                                    devig = requests.get(devigurl)
                                    devig = devig.json()
                                    print("FD - {}: {}".format(r["runnerName"], r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"]))
                                    DevigLink = "http://crazyninjamike.com/Public/sportsbooks/sportsbook_devigger.aspx?autofill=1&LegOdds={}%2f7%25&FinalOdds={}".format(r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], p["americanOdds"])
                                    if "Final" in devig:
                                        fullKelly = devig["Final"]["Kelly_Full"]
                                        bankroll = request.cookies.get('Bankroll')
                                        kelly = request.cookies.get('KellyMultiplier')
                                        if bankroll is None:
                                            bankroll = 1000
                                        if kelly is None:
                                            kelly = .25
                                        betSize = int(bankroll) * .01 * float(kelly) * fullKelly
                                        Line = {"Name": name, "FanduelOdds": r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], "MGMOdds": p["americanOdds"], "EVPercentage": '{:.2%}'.format(devig["Final"]["EV_Percentage"]), "FullKelly": "{:.2f}".format(devig["Final"]["Kelly_Full"]), "DevigLink": DevigLink, "BetSize": betSize}
                                        game["Lines"].append(Line)
                if(len(game["Lines"]) > 0):
                    games.append(game)

    return games

def getPitcherH2H():
    games = list()
    fd_all_url = "https://sbapi.il.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FChicago"
    mgm_all_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixtures?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&fixtureTypes=Standard&state=Latest&offerMapping=MainMarkets&sortBy=FixtureStage&competitionIds=75&virtualCompetitionIds="
    mgm_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    fd_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'cache-control': 'no-cache',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
        }
    mgm_all = requests.get(mgm_all_url, headers = mgm_headers)
    mgm_all = mgm_all.json()
    fd_all = requests.get(fd_all_url, headers = fd_headers)
    fd_all = fd_all.json()
    for i in mgm_all["fixtures"]:
        id = i["id"]
        if len(i["participants"]) > 0:
            #print(i["startDate"])
            #2023-07-25T22:40:00Z
            mgmGameStart = datetime.strptime(i["startDate"], '%Y-%m-%dT%H:%M:%SZ')
            away = i["participants"][0]["name"]["short"]
            #print(away)
            #match away team to one competitor from fd_all[attachments][events]
            for fd in fd_all["attachments"]["events"]:
                fdGameStart = datetime.strptime(fd_all["attachments"]["events"][fd]["openDate"], '%Y-%m-%dT%H:%M:%S.%fZ')
                if (away in fd_all["attachments"]["events"][fd]["name"]) and (mgmGameStart.day == fdGameStart.day) and (mgmGameStart.hour == fdGameStart.hour):
                    #print("FD: {}".format(fd_all["attachments"]["events"][fd]["openDate"]))
                    #print(away)
                    #create game, may be scrapped later if no lines are added
                    game = {"Name": fd_all["attachments"]["events"][fd]["name"], "AwayPitcher": "", "HomePitcher": "", "AwayOdds": "", "HomeOdds": "", "AwayFDAlts": list(), "HomeFDAlts": list(), "mult": "", "add": "", "power": ""}
                    #print(fd_all["attachments"]["events"][fd]["name"])
                    fd_one_id = fd_all["attachments"]["events"][fd]["eventId"]
                    #break
            fd_one_url = "https://sbapi.il.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={}&tab=pitcher-props".format(fd_one_id)
            mgm_one_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixture-view?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&offerMapping=All&scoreboardMode=Full&fixtureIds={}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false&useRegionalisedConfiguration=true&includeRelatedFixtures=true".format(id)
            mgm = requests.get(mgm_one_url, headers = mgm_headers)
            fd = requests.get(fd_one_url, headers= fd_headers)
            fd=fd.json()        
            fd = fd["attachments"]["markets"]
            data =[]
            for i in fd:
                if "Alt Strikeouts" in fd[i]["marketName"]:
                    data.append(fd[i])
            mgm=mgm.json()
            if "linkedFixture" in mgm:
                for i in mgm["linkedFixture"]["optionMarkets"]:
                    if (i["name"]["value"] == "Most Ks" and i["status"] != "Suspended"):
                         #Options[2]
                         #options[0].name.value
                         #options[0].price.americanodds
                         if len(data) == 2:
                            HomeFDAlts = list()
                            AwayFDAlts = list()
                            awayPitcher = data[0]["marketName"].split("-")[0].rstrip()
                            homePitcher = data[1]["marketName"].split("-")[0].rstrip()
                            game["AwayPitcher"] = awayPitcher
                            game["HomePitcher"] = homePitcher
                            a = i["options"][0]["name"]["value"]
                            if awayPitcher == i["options"][0]["name"]["value"]:
                                game["AwayOdds"] = i["options"][0]["price"]["americanOdds"] if "-" in str(i["options"][0]["price"]["americanOdds"]) else "+{}".format(i["options"][0]["price"]["americanOdds"])
                                game["HomeOdds"] = i["options"][1]["price"]["americanOdds"] if "-" in str(i["options"][1]["price"]["americanOdds"]) else "+{}".format(i["options"][1]["price"]["americanOdds"])
                            else:
                                game["AwayOdds"] = i["options"][1]["price"]["americanOdds"] if "-" in str(i["options"][1]["price"]["americanOdds"]) else "+{}".format(i["options"][1]["price"]["americanOdds"])
                                game["HomeOdds"] = i["options"][0]["price"]["americanOdds"] if "-" in str(i["options"][0]["price"]["americanOdds"]) else "+{}".format(i["options"][0]["price"]["americanOdds"])
                            for line in data[0]["runners"]:
                                Line = { "Label": line["runnerName"], "Odds": line["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"] }
                                game["AwayFDAlts"].append(Line)
                            for line in data[1]["runners"]:                 
                                Line = { "Label": line["runnerName"], "Odds": line["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"] }           
                                game["HomeFDAlts"].append(Line)
                            games.append(game)
    return games

def CZRvsFD():    
    games = list()
    czr_all_url = "https://api.americanwagering.com/regions/us/locations/il/brands/czr/sb/v3/sports/baseball/events/schedule"
    fd_all_url = "https://sbapi.il.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FChicago"
    czr_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    fd_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'cache-control': 'no-cache',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
        }
    czr_all = requests.get(czr_all_url, headers = czr_headers)
    czr_all = czr_all.json()
    fd_all = requests.get(fd_all_url, headers = fd_headers)
    fd_all = fd_all.json()
    Games = {}
    if "competitions" in czr_all:
        events = czr_all["competitions"][0]["events"]
        for event in events:
            if("currentHomeStartingPitcher" in event["metadata"]):
                game = {"Name": event["name"].replace("|", ""), "HomePitcher": event["metadata"]["currentHomeStartingPitcher"].split(" ")[1], "AwayPitcher": event["metadata"]["currentAwayStartingPitcher"].split(" ")[1], "Lines": list(), "data": list() }
                czr_one_id = event["id"]            
                czrGameStart = datetime.strptime(event["startTime"], '%Y-%m-%dT%H:%M:%SZ')
                away = event["name"].split("|")[1]
                for fd in fd_all["attachments"]["events"]:                
                    fd_one_id = None
                    fdGameStart = datetime.strptime(fd_all["attachments"]["events"][fd]["openDate"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    if (away in fd_all["attachments"]["events"][fd]["name"]) and (czrGameStart.day == fdGameStart.day) and (czrGameStart.hour == fdGameStart.hour):
                        #print("FD: {}".format(fd_all["attachments"]["events"][fd]["openDate"]))
                        #print(away)
                        #create game, may be scrapped later if no lines are added
                        #print(fd_all["attachments"]["events"][fd]["name"])
                        fd_one_id = fd_all["attachments"]["events"][fd]["eventId"]
                        break
                if fd_one_id:               
                    czr_one_url = "https://api.americanwagering.com/regions/us/locations/il/brands/czr/sb/v3/events/{}".format(czr_one_id)
                    czr = requests.get(czr_one_url, headers = czr_headers)
                    fd_one_url = "https://sbapi.il.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={}&tab=pitcher-props".format(fd_one_id)
                    fd = requests.get(fd_one_url, headers = fd_headers)
                    fd=fd.json()        
                    fd = fd["attachments"]["markets"]
                    data =[]            
                    for i in fd:
                        if "Alt Strikeouts" in fd[i]["marketName"]:
                            for runner in fd[i]["runners"]:
                                runnerNameSplit = runner["runnerName"].split(" ")
                                line =  { "Book": "FD", "LastName": runnerNameSplit[1], "Line": int(runnerNameSplit[2].replace("+","")), "Price": runner["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"]  }
                                game["Lines"].append(line)
                    czr = czr.json()
                    if "markets" in czr:
                        for market in czr["markets"]:
                            if "Alternate Strikeouts" in market["displayName"]:
                                nameSplit = market["name"].split("|")
                                line = { "Book": "CZR", "LastName": nameSplit[1].split(" ")[1], "Line": int(nameSplit[3].split(" ")[2].replace("+","")), "Price": market["selections"][0]["price"]["a"]  }
                        
                                game["Lines"].append(line)        
                        game["Lines"] = (sorted(game["Lines"], key=lambda x: x["Line"]))
                        games.append(game)
        #games = {k:v for (k,v) in games.items() if filter_string in k}
        for game in games:
            for number in range(3,12):
                    awayRowCZR = list(filter(lambda g: g['Line'] == number and g['LastName'] in game["AwayPitcher"] and g['Book'] == 'CZR', game["Lines"]))
                    homeRowCZR = list(filter(lambda g: g['Line'] == number and g['LastName'] in game["HomePitcher"] and g['Book'] == 'CZR', game["Lines"]))
                    awayRowFD = list(filter(lambda g: g['Line'] == number and g['LastName'] in game["AwayPitcher"] and g['Book'] == 'FD', game["Lines"]))
                    homeRowFD = list(filter(lambda g: g['Line'] == number and g['LastName'] in game["HomePitcher"] and g['Book'] == 'FD', game["Lines"]))
                    game["data"].append({
                        "Line": number, 
                        "awayPitcher": game["AwayPitcher"], 
                        "homePitcher": game["HomePitcher"], 
                        "awayCZR": awayRowCZR[0]["Price"] if len(awayRowCZR) > 0 else "N/A",
                        "awayFD": awayRowFD[0]["Price"] if len(awayRowFD) > 0 else "N/A", 
                        "homeCZR": homeRowCZR[0]["Price"] if len(homeRowCZR) > 0 else "N/A", 
                        "homeFD": homeRowFD[0]["Price"] if len(homeRowFD) > 0 else "N/A"
                        })
       #xyz= list(filter(lambda g: g['Line'] == 1, g["Lines"]))
    return games



@app.route('/savesettings', methods = ['GET', 'POST'])
def setcookie():    
      # Initializing response object
      bankroll = request.form['Bankroll']
      kelly = request.form['Kelly']
      resp = make_response('Settings have been updated. Refresh page to view updated bet sizes') 
      resp.set_cookie('KellyMultiplier', kelly, max_age=99999999)
      resp.set_cookie('Bankroll', bankroll, max_age=99999999)
      return resp

@app.route('/getcookie')
def getcookie():
    k = request.cookies.get('KellyMultiplier')
    b = request.cookies.get('Bankroll')
    return 'Multiplier: '+ k + ' Bankroll: ' + b

@app.route('/writetosheet')
def WriteToSheet():
    gc = pygsheets.authorize(service_file='./creds.json')
    sh = gc.open('Pitcher Duels')
    wks = sh[0]
    wks.clear()
    games = list()
    fd_all_url = "https://sbapi.il.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&pbHorizontal=false&includeEnhancedScan=true&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FChicago"
    mgm_all_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixtures?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&fixtureTypes=Standard&state=Latest&offerMapping=MainMarkets&sortBy=FixtureStage&competitionIds=75&virtualCompetitionIds="
    mgm_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    fd_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'cache-control': 'no-cache',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
        }
    mgm_all = requests.get(mgm_all_url, headers = mgm_headers)
    mgm_all = mgm_all.json()
    fd_all = requests.get(fd_all_url, headers = fd_headers)
    fd_all = fd_all.json()

    for i in mgm_all["fixtures"]:
        id = i["id"]
        if len(i["participants"]) > 0:
            #print(i["startDate"])
            #2023-07-25T22:40:00Z
            mgmGameStart = datetime.strptime(i["startDate"], '%Y-%m-%dT%H:%M:%SZ')
            away = i["participants"][0]["name"]["short"]
            print(away)
            #match away team to one competitor from fd_all[attachments][events]
            for fd in fd_all["attachments"]["events"]:
                fd_one_id = None
                fdGameStart = datetime.strptime(fd_all["attachments"]["events"][fd]["openDate"], '%Y-%m-%dT%H:%M:%S.%fZ')
                if (away in fd_all["attachments"]["events"][fd]["name"]) and (mgmGameStart.day == fdGameStart.day) and (mgmGameStart.hour == fdGameStart.hour):
                    #print("FD: {}".format(fd_all["attachments"]["events"][fd]["openDate"]))
                    #print(away)
                    #create game, may be scrapped later if no lines are added
                    game = {"Name": fd_all["attachments"]["events"][fd]["name"], "Lines": list(), "AwayPitcher": "", "HomePitcher": ""}
                    gameName = fd_all["attachments"]["events"][fd]["name"]
                    #print(fd_all["attachments"]["events"][fd]["name"])
                    fd_one_id = fd_all["attachments"]["events"][fd]["eventId"]
                    break
            if fd_one_id:                
                fd_one_url = "https://sbapi.il.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={}&tab=popular".format(fd_one_id)
                mgm_one_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixture-view?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&offerMapping=All&scoreboardMode=Full&fixtureIds={}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false&useRegionalisedConfiguration=true".format(id)
                mgm = requests.get(mgm_one_url, headers = mgm_headers)
                fd = requests.get(fd_one_url, headers = fd_headers)
                fd=fd.json()       
                fd = fd["attachments"]["markets"]
                data =[]
                for i in fd:
                    if "Alt Strikeouts" in fd[i]["marketName"]:
                        data.append(fd[i])
                mgm=mgm.json()
                for i in mgm["fixture"]["optionMarkets"]:
                    if i["name"]["value"] == "Pitcher's Duel":
                        mgm_results = i["options"]
                        for q in mgm_results:
                            #print(len(data))
                            if len(data) == 2:                            
                                game["AwayPitcher"] = data[0]["marketName"].split("-")[0]
                                game["HomePitcher"] = data[1]["marketName"].split("-")[0]
                                oddsOne = 0
                                oddsTwo = 0
                                if "5+" in q["name"]["value"]:
                                    x=len(data[0]["runners"])
                                    if len(data[0]["runners"]) > 2 and len(data[1]["runners"]) > 2:
                                        oddsOne = str(data[0]["runners"][2]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                        oddsTwo = str(data[1]["runners"][2]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                if "6+" in q["name"]["value"]:
                                    if len(data[0]["runners"]) > 3 and len(data[1]["runners"]) > 3:
                                        oddsOne = str(data[0]["runners"][3]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                        oddsTwo = str(data[1]["runners"][3]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                if "7+" in q["name"]["value"]:
                                    if len(data[0]["runners"]) > 4 and len(data[1]["runners"]) > 4:
                                        oddsOne = str(data[0]["runners"][4]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                        oddsTwo = str(data[1]["runners"][4]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                if "8+" in q["name"]["value"]:
                                    if len(data[0]["runners"]) > 5 and len(data[1]["runners"]) > 5:
                                        oddsOne = str(data[0]["runners"][5]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                        oddsTwo = str(data[1]["runners"][5]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                finalOdds = str(q["price"]["americanOdds"])
                                devigurl = "https://api.crazyninjaodds.com/api/devigger/v1/sportsbook_devigger.aspx?api=open&legodds={}/7%,{}/7%&finalodds={}&devigmethod=4&args=ev_p,kelly".format(oddsOne, oddsTwo, finalOdds)
                                devig = requests.get(devigurl)
                                devig = devig.json()
                                if "Final" in devig:
                                    #if devig["Final"]["EV_Percentage"] > 0:
                                        #add to game

                                        #format odds to have a "+" at the start if they don't start with "-"
                                        oddsOne = oddsOne if "-" in oddsOne else "+{}".format(oddsOne)
                                        oddsTwo = oddsTwo if "-" in oddsTwo else "+{}".format(oddsTwo)
                                        finalOdds = finalOdds if "-" in finalOdds else "+{}".format(finalOdds)

                                        #create CNM Devig link
                                        #DevigLink = "http://crazyninjamike.com/Public/sportsbooks/sportsbook_devigger.aspx?autofill=1&LegOdds={}%2f7%25%2c{}%2f7%25&FinalOdds={}".format(oddsOne,oddsTwo,finalOdds)
                                        fullKelly = devig["Final"]["Kelly_Full"]
                                        bankroll = request.cookies.get('Bankroll')
                                        kelly = request.cookies.get('KellyMultiplier')
                                        if bankroll is None:
                                            bankroll = 1000
                                        if kelly is None:
                                            kelly = .25
                                        #betSize = int(bankroll) * .01 * float(kelly) * fullKelly
                                    
                                        Line = {"Game_Name": gameName, "Bet_Name": q["name"]["value"], "MGM_Odds": finalOdds, "AwayPitcherOdds": oddsOne, "HomePitcherOdds": oddsTwo, "EVPercentage": '{:.2%}'.format(devig["Final"]["EV_Percentage"]), "BetSize": fullKelly}
                                        games.append(Line)

                                        #"EV": devig["Final"]["EV_Percentage"], "Kelly": devig["Final"]["Kelly_Full"]
                                        #print(q["name"]["value"])
                                        #print(q["americanOdds"])
                                        #print(devig["Final"]["EV_Percentage"])
                                        #print(devig["Final"]["Kelly_Full"])
                            #print(q["name"]["value"])
                            #print(q["americanOdds"])
                        #if(len(game["Lines"]) > 0):
                            #games.append(game)
                        #addGame = "true"
                        #for line in game["Lines"]:
                            #if '-' not in line["EVPercentage"]:
                                #addGame="true"
                        #if addGame == "true":
                            #games.append(game)
    df = pd.DataFrame(games)              
    wks.set_dataframe(df,(1,1))
    response = app.response_class(
        response = "Sheet updated",
        status = 200,
        mimetype='application/json'
        )
    return response
if __name__ == '__main__':
   app.run(debug=False,host='0.0.0.0')
