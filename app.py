import os
import requests
import json
from datetime import datetime
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
    games = getData()
    resp = make_response(render_template(
        'index.html',
        title='Home Page',
        games = games,
        year=datetime.now().year,
        bankroll = bankroll,
        kelly = kelly
    ))
    resp.set_cookie('Bankroll', bankroll)
    resp.set_cookie('KellyMultiplier', kelly)
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
    resp.set_cookie('Bankroll', bankroll)
    resp.set_cookie('KellyMultiplier', kelly)
    return resp

@app.route('/data')
def data():
    data = getData()
    response = app.response_class(
        response = json.dumps(data),
        status = 200,
        mimetype='application/json'
        )
    return response


def getData():
    """Renders the contact page."""
    games = list()
    fd_all_url = "https://sbapi.il.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FChicago"
    mgm_all_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixtures?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&fixtureTypes=Standard&state=Latest&offerMapping=MainMarkets&sortBy=FixtureStage&competitionIds=75&virtualCompetitionIds="
    mgm_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    mgm_all = requests.get(mgm_all_url, headers = mgm_headers)
    mgm_all = mgm_all.json()
    fd_all = requests.get(fd_all_url)
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
                    game = {"Name": fd_all["attachments"]["events"][fd]["name"], "Lines": list(), "AwayPitcher": "", "HomePitcher": ""}
                    #print(fd_all["attachments"]["events"][fd]["name"])
                    fd_one_id = fd_all["attachments"]["events"][fd]["eventId"]
                    #break
            fd_one_url = "https://sbapi.il.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={}&tab=pitcher-props".format(fd_one_id)
            mgm_one_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixture-view?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&offerMapping=All&scoreboardMode=Full&fixtureIds={}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false&useRegionalisedConfiguration=true".format(id)
            mgm = requests.get(mgm_one_url, headers = mgm_headers)
            fd = requests.get(fd_one_url)
            fd=fd.json()        
            fd = fd["attachments"]["markets"]
            data =[]
            for i in fd:
                if "Alt Strikeouts" in fd[i]["marketName"]:
                    data.append(fd[i])
            mgm=mgm.json()
            for i in mgm["fixture"]["games"]:
                if i["name"]["value"] == "Pitcher's Duel":
                    mgm_results = i["results"]
                    for q in mgm_results:
                        #print(len(data))
                        if len(data) == 2:                            
                            game["AwayPitcher"] = data[0]["marketName"].split("-")[0]
                            game["HomePitcher"] = data[1]["marketName"].split("-")[0]
                            oddsOne = 0
                            oddsTwo = 0
                            if "5+" in q["name"]["value"]:
                                oddsOne = str(data[0]["runners"][2]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                oddsTwo = str(data[1]["runners"][2]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                            if "6+" in q["name"]["value"]:
                                oddsOne = str(data[0]["runners"][3]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                oddsTwo = str(data[1]["runners"][3]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                            if "7+" in q["name"]["value"]:
                                oddsOne = str(data[0]["runners"][4]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                oddsTwo = str(data[1]["runners"][4]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                            #if "8+" in q["name"]["value"]:
                                #oddsOne = str(data[0]["runners"][5]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                                #oddsTwo = str(data[1]["runners"][5]["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"])
                            finalOdds = str(q["americanOdds"])
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
                                    DevigLink = "http://crazyninjamike.com/Public/sportsbooks/sportsbook_devigger.aspx?autofill=1&LegOdds={}%2f7%25%2c{}%2f7%25&FinalOdds={}".format(oddsOne,oddsTwo,finalOdds)
                                    fullKelly = devig["Final"]["Kelly_Full"]
                                    bankroll = request.cookies.get('Bankroll')
                                    kelly = request.cookies.get('KellyMultiplier')
                                    if bankroll is None:
                                        bankroll = 1000
                                    if kelly is None:
                                        kelly = .25
                                    betSize = int(bankroll) * .01 * float(kelly) * fullKelly
                                    
                                    Line = {"Name": q["name"]["value"], "Odds": finalOdds, "AwayPitcherOdds": oddsOne, "HomePitcherOdds": oddsTwo, "EVPercentage": '{:.2%}'.format(devig["Final"]["EV_Percentage"]), "BetSize": '${:,.2f}'.format(betSize), "DevigLink": DevigLink}
                                    game["Lines"].append(Line)

                                    #"EV": devig["Final"]["EV_Percentage"], "Kelly": devig["Final"]["Kelly_Full"]
                                    #print(q["name"]["value"])
                                    #print(q["americanOdds"])
                                    #print(devig["Final"]["EV_Percentage"])
                                    #print(devig["Final"]["Kelly_Full"])
                        #print(q["name"]["value"])
                        #print(q["americanOdds"])
                    #if(len(game["Lines"]) > 0):
                        #games.append(game)
                    addGame = "false"
                    for line in game["Lines"]:
                        if '-' not in line["EVPercentage"]:
                            addGame="true"
                    if addGame == "true":
                        games.append(game)
                            
    print(games)
    return games

def getPitcherProps():
    games = list()
    fd_all_url = "https://sbapi.il.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FChicago"
    mgm_all_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixtures?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&fixtureTypes=Standard&state=Latest&offerMapping=MainMarkets&sortBy=FixtureStage&competitionIds=75&virtualCompetitionIds="
    mgm_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    mgm_all = requests.get(mgm_all_url, headers = mgm_headers)
    mgm_all = mgm_all.json()
    fd_all = requests.get(fd_all_url)
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
            mgm_one_url = "https://sports.il.betmgm.com/cds-api/bettingoffer/fixture-view?x-bwin-accessid=ZTg4YWEwMTgtZTlhYy00MWRkLWIzYWYtZjMzODI5ZDE0Mjc5&lang=en-us&country=US&userCountry=US&subdivision=US-Illinois&offerMapping=All&scoreboardMode=Full&fixtureIds={}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false&useRegionalisedConfiguration=true".format(id)
            mgm = requests.get(mgm_one_url, headers = mgm_headers)
            fd = requests.get(fd_one_url)
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
                                        Line = {"Name": name, "FanduelOdds": r["winRunnerOdds"]["americanDisplayOdds"]["americanOdds"], "MGMOdds": p["americanOdds"], "EVPercentage": '{:.2%}'.format(devig["Final"]["EV_Percentage"]), "BetSize": '${:,.2f}'.format(betSize), "DevigLink": DevigLink}
                                        game["Lines"].append(Line)
                if(len(game["Lines"]) > 0):
                    games.append(game)

    return games
@app.route('/savesettings', methods = ['GET', 'POST'])
def setcookie():    
      # Initializing response object
      bankroll = request.form['Bankroll']
      kelly = request.form['Kelly']
      resp = make_response('Settings have been updated') 
      resp.set_cookie('KellyMultiplier', kelly)
      resp.set_cookie('Bankroll', bankroll)
      return resp

@app.route('/getcookie')
def getcookie():
    k = request.cookies.get('KellyMultiplier')
    b = request.cookies.get('Bankroll')
    return 'Multiplier: '+ k + ' Bankroll: ' + b
if __name__ == '__main__':
   app.run(debug=False,host='0.0.0.0')
