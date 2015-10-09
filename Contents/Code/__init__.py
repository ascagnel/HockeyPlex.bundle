# hockeyPlex
# hockeyStreams.com Plugin for Plex Media Center
# by Mark Freden m@sitticus.com
# updated by Kevin Centeno @devteno and Alfredo Gomez github/agomezgz
# Version .9
# Dec 10, 2015

KEY = 'e00a9c3af1391138c121d6d669f54483'

TITLE = 'HockeyPlex 0.9'
PREFIX = '/video/hockeyplex09'

ART = 'wethenorth.jpg'
ICON = 'icon-default.png'
LIVE_ICON = ''
ONDEMAND_ICON = ''
TOKEN = None

TEAM_NAMES = 'teams.json'

TITLE_LIVEGAMES = 'Live Games'
TITLE_ONDEMANDGAMES = 'On Demand'
TITLE_PREFERENCES = 'Preferences'
TITLE_LOGIN = 'Log In'

URL_LOGIN = 'https://api.hockeystreams.com/Login'
URL_LIVEGAMES = 'https://api.hockeystreams.com/GetLive?token=%s'
URL_LIVESTREAMS = 'https://api.hockeystreams.com/GetLiveStream?id=%s&token=%s'
URL_ONDEMANDGAMES = 'https://api.hockeystreams.com/GetOnDemand?date=%s&token=%s'
URL_ONDEMANDDATES = 'https://api.hockeystreams.com/GetOnDemandDates?token=%s'
URL_ONDEMANDSTREAM = 'https://api.hockeystreams.com/GetOnDemandStream?id=%s&token=%s'
URL_PREVIEW = "http://s.hscontent.com/preview/preview_bsHD.m3u8?token="
URL_GAMEOFF = ''
URL_REPO = ''
URL_LOGOREPO = ''
URL_ARENAREPO = ''

# Import urlparse for encodeUrlToken
from urlparse import urlparse

###################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = TITLE
    DirectoryObject.thumb = R(ICON)

    ValidatePrefs()

###################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer(no_cache=True)

    # Only show menus if TOKEN has been successfully set
    if TOKEN != None:
        oc.add(DirectoryObject(
            key=Callback(LiveGamesMenu),
            title=TITLE_LIVEGAMES,
            thumb=R(LIVE_ICON)
        ))
        oc.add(DirectoryObject(
            key=Callback(OnDemandDatesMenu),
            title=TITLE_ONDEMANDGAMES,
            thumb=R(ONDEMAND_ICON)
        ))

        oc.add(PrefsObject(
            title=TITLE_PREFERENCES)
        )
    else:
        oc.add(PrefsObject(
            title=TITLE_LOGIN
        ))

        oc.add(GetStream(URL_PREVIEW, "Preview", URL_PREVIEW, R(ICON), R(ICON), "Preview feed", False, "hls"))

    return oc

###################################################################################################
@route(PREFIX + '/livegamesmenu')
def LiveGamesMenu():
    title = TITLE_LIVEGAMES
    url = URL_LIVEGAMES % TOKEN

    oc = ObjectContainer(title2=title, no_cache=True)

    # Loop thru videos array returned from GetLiveGames
    for video in GetLiveGames(url):
        (game_id, title, logo, arena, summary, isPlaying) = video

        # If there was an error, display it
        if game_id == 0:
            return (ObjectContainer(header="Error", message=title))
        else:
            #oc.add(GetStream(game_id, title, srcUrl, logo, arena, summary))
            oc.add(DirectoryObject(
                    key=Callback(GetLiveGameStreams, game_id=game_id, title=title, isPlaying=isPlaying, summary=summary),
                    title=title
                ))

    oc.add(PrefsObject(
        title=TITLE_PREFERENCES)
    )

    return oc

###################################################################################################
@route(PREFIX + "/getlivegames")
def GetLiveGames(url):
    # Set up our array to return
    videos = []

    # Get data from server
    game_json = JSON.ObjectFromURL(url)

    if game_json["status"] == "Success":

        # Get Prefs
        leagueFilter = Prefs["leaguefilter"]
        # quality = Prefs["quality"]

        # Loop thru each to build videos meta
        for video in game_json["schedule"]:

            # Set flag to not add video
            addVid = False

            # Check if league filter is on and filter results
            if leagueFilter == "All":
                addVid = True
            else:
                # Change this to "contains" so NHL Pre-Season Shows Up
                if video["event"] == leagueFilter:
                    addVid = True
                else:
                    Log(" Filtering Out Game ID: " + video["id"])

            # If the video should be added, build the meta
            if addVid:
                populateVideoArray(videos, video, True)

    else:

        Log(" Get Live Games ERROR - " + game_json["msg"])

        # Send back an empty video with the Failed message so we can display a dialog
        if game_json["status"] == "Failed":
            videos.append([0, game_json["msg"], "", "", "", ""])

    return videos


###################################################################################################
@route(PREFIX + '/getlivegamestreams')
def GetLiveGameStreams(game_id, title, isPlaying, summary):

    oc = ObjectContainer(title2=title, no_cache=True)

    # Get data from server
    url = URL_LIVESTREAMS % (game_id, TOKEN)
    url = url + getServerLocation()

    json = JSON.ObjectFromURL(url)

    quality = Prefs['quality']

    if quality == 'High':
        hlsUrl = json['nonDVRHD'][0]['src']
        #rtmpUrl = json['TrueLiveHD'][0]['src']

        oc.add(GetStream(hlsUrl, "Regular Stream", hlsUrl, R(ICON), R(ART), summary, False, "hls"))
        #oc.add(GetStream(rtmpUrl, "TrueLive Stream", rtmpUrl, R(ICON), R(ART), summary, False, "rtmp"))
    else:
        hlsUrl = json['nonDVRSD'][0]['src']
        #rtmpUrl = json['TrueLiveSD'][0]['src']

        oc.add(GetStream(hlsUrl, "Regular Stream", hlsUrl, R(ICON), R(ART), summary, False, "hls"))
        #oc.add(GetStream(rtmpUrl, "TrueLive Stream", rtmpUrl, R(ICON), R(ART), summary, False, "rtmp"))

    oc.add(PrefsObject(
            title=TITLE_PREFERENCES)
        )

    return oc

###################################################################################################
@route(PREFIX + '/ondemanddatesmenu')
def OnDemandDatesMenu():
    oc = ObjectContainer(title2='On Demand Dates', no_cache=True)

    # Read the dates data from the server
    url = URL_ONDEMANDDATES % TOKEN
    json = JSON.ObjectFromURL(url)

    # Make sure there wasn't an error
    if json["status"] == "Success":

        # Loop thru the array of dates return from the server
        for gameDate in json['dates']:

            if gameDate: # Make sure it's not empty
                oc.add(DirectoryObject(
                    key=Callback(OnDemandGamesMenu, gameDate=gameDate),
                    title=FormatDate(gameDate),
                    thumb=R(ONDEMAND_ICON)
                ))
    else:
        # Display the error if there was one
        return (ObjectContainer(header="Error", message=json["msg"]))

    oc.add(PrefsObject(
        title=TITLE_PREFERENCES)
    )

    return oc

###################################################################################################
@route(PREFIX + '/ondemandgamesmenu')
def OnDemandGamesMenu(gameDate):
    title = 'On Demand Games For ' + gameDate
    url = URL_ONDEMANDGAMES % (gameDate, TOKEN)

    oc = ObjectContainer(title2=title, no_cache=True)

    # Loop thru the array return by GetOnDemandGames
    for video in GetOnDemandGames(url):
        (game_id, title, logo, arena, summary, isPlaying) = video

        oc.add(DirectoryObject(
            key=Callback(OnDemandStreamMenu, game_id=game_id, title=title, logo=logo, arena=arena, summary=summary),
            title=title,
            thumb=URL_LOGOREPO + logo,
            art=URL_ARENAREPO + arena,
            summary=summary
        ))

    oc.add(PrefsObject(
        title=TITLE_PREFERENCES)
    )

    return oc

###################################################################################################
@route(PREFIX + '/ondemandstreammenu')
def OnDemandStreamMenu(game_id, title, logo, arena, summary):
    serverLocation = getServerLocation()
    url = URL_ONDEMANDSTREAM % (game_id, TOKEN + serverLocation)
    game_json = JSON.ObjectFromURL(url)

    # Get Prefs
    quality = Prefs['quality']

    oc = ObjectContainer(title2=title, no_cache=True)

    homeTeam = game_json['homeTeam']
    awayTeam = game_json['awayTeam']

    if homeTeam:
        gameName = "Full Game"
    else:
        gameName = "Watch " + awayTeam

    ### Set vid quality chosen in prefs
    # if game_json['HDstreams'][0]['src']: HD = game_json['HDstreams'][0]['src']
    # if game_json['SDstreams'][0]['src']: SD = game_json['SDstreams'][0]['src']

    # Monkey Patch:  API is busted, returning mp4s in HLS streams
    if game_json['HDstreams'][0]['src']: HD = game_json['streams'][2]['src']
    if game_json['SDstreams'][0]['src']: SD = game_json['streams'][2]['src']

    if HD and quality == 'High':
        oc.add(GetStream(HD, gameName, HD, logo, arena, summary, False, "mp4"))
    else:
        oc.add(GetStream(SD, gameName, SD, logo, arena, summary, False, "mp4"))

    ### Highlights
    homeHighlights = game_json['highlights'][0]['homeSrc']
    awayHighlights = game_json['highlights'][0]['awaySrc']

    if homeHighlights == awayHighlights and homeHighlights != "" and awayHighlights != "":
        oc.add(GetStream(homeHighlights, "Highlights", homeHighlights, logo, arena, summary, False, "mp4"))
    else:
        if homeHighlights:
            oc.add(GetStream(homeHighlights, homeTeam + " Highlights", homeHighlights, logo, arena, summary, False, "mp4"))
        if awayHighlights:
            oc.add(GetStream(awayHighlights, awayTeam + " Highlights", awayHighlights, logo, arena, summary, False, "mp4"))

    oc.add(PrefsObject(
        title=TITLE_PREFERENCES)
    )
    return oc

###################################################################################################
@route(PREFIX + '/getondemandgames')
def GetOnDemandGames(url):
    videos = []

    # Get data from server
    game_json = JSON.ObjectFromURL(url)

    if 'ondemand' in game_json:
        for video in game_json['ondemand']:

            # If there isn't an iStream, don't list it
            if video['isiStream'] == 1:

                populateVideoArray(videos, video)

    return videos

###################################################################################################
@route(PREFIX + '/getstream', include_container = bool)
def GetStream(game_id, title1, url, thumb, art, summary, include_container=False, streamType="hls"):
    Log("GetStream Game: " + str([game_id, title1, url, thumb, art, summary]))

    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2

    if streamType == "mp4":
        vco = VideoClipObject(
            key=Callback(GetStream, game_id=game_id, title1=title1, url=url, thumb=thumb, art=art, summary=summary,
                         include_container=True, streamType="mp4"),
            rating_key=game_id,
            title=title1,
            art=URL_ARENAREPO + art,
            thumb=URL_LOGOREPO + thumb,
            summary=summary,
            items=[
                MediaObject(
                    parts=[
                        PartObject(key=Callback(PlayVideo, url=url))
                    ],
                    container = container,
                    video_codec = video_codec,
                    audio_codec = audio_codec,
                    audio_channels = audio_channels,
                    optimized_for_streaming=True
                )
            ]
        )

    elif streamType == "rtmp":
        fullurl = url.split(" ")

        if len(fullurl) > 1:
            rtmpurl = fullurl[0]
            swfurl = fullurl[1]
        else:
            rtmpurl = ""
            swfurl = ""

        rtmpurl = rtmpurl.replace("rtmp:////", "rtmp://")
        swfurl = swfurl.replace("'", "").replace("swfUrl=", "")

        vco = VideoClipObject(
            key=Callback(GetStream, game_id=game_id, title1=title1, url=url, thumb=thumb, art=art, summary=summary,
                         include_container=True, streamType="rtmp"),
            rating_key=game_id,
            title=title1,
            art=URL_ARENAREPO + art,
            thumb=URL_LOGOREPO + thumb,
            summary=summary,
            items=[
                MediaObject(
                    parts=[
                        PartObject(key=RTMPVideoURL(url=rtmpurl, swfurl=swfurl, live=True))
                    ],
                    optimized_for_streaming=True
                )
            ]
        )
    elif streamType == "hls":
        vco = VideoClipObject(
            key=Callback(GetStream, game_id=game_id, title1=title1, url=url, thumb=thumb, art=art, summary=summary,
                         include_container=True, streamType="hls"),
            rating_key=game_id,
            title=title1,
            art=URL_ARENAREPO + art,
            thumb=URL_LOGOREPO + thumb,
            summary=summary,
            items=[
                MediaObject(
                    optimized_for_streaming=True,
                    parts=[
                        PartObject(key=HTTPLiveStreamURL(url=url))
                    ]
                )
            ]
        )

    if include_container:
        return ObjectContainer(objects=[vco])
    else:
        return vco

@route(PREFIX + '/playvideo')
@indirect
def PlayVideo(url):
    return IndirectResponse(VideoClipObject, key=url)

###################################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():
    # When prefs get saved, update Token
    global TOKEN

    TOKEN = GetToken()

    # Assume there was an error
    if TOKEN == None:
        return ObjectContainer(header="Login Error",
                               message="Make sure your username and password are correct.")

###################################################################################################
@route(PREFIX + '/gettoken')
def GetToken():
    # Get the username and pass from the prefs
    user = Prefs['username']
    password = Prefs['password']

    data = {'username': user, 'password': password, 'key': KEY}

    # Get the token from BS Login API
    try:
        json = JSON.ObjectFromURL(URL_LOGIN, data)
        ## How can I get the HTTP Error and the json? ##

        return json['token']

    except:
        return None

###################################################################################################
@route(PREFIX + '/encodurltoken')
def encodeUrlToken(url):
    # Encode the token param so it doesn't fail on 3rd party/web devices

    parsed = urlparse(url)

    encodedToken = String.Quote(parsed[4], True)

    encUrl = parsed[0] + '://' + parsed[1] + parsed[2] + "?" + encodedToken

    return encUrl

###################################################################################################
@route(PREFIX + '/formatdate')
def FormatDate(theDate):
    # Import date and time modules
    from datetime import date, timedelta
    import time

    # Get and make today and yesterday strings for comparison to theDate
    today = date.today()
    todayStr = today.strftime("%m/%d/%Y")
    yesterday = today - timedelta(1)
    yesterdayStr = yesterday.strftime("%m/%d/%Y")

    # If theDate is today or tomorrow return that
    if theDate == todayStr:
        return "Today"
    elif theDate == yesterdayStr:
        return "Yesterday"
    else:
        # Convert the text to a time obj
        c = time.strptime(theDate, "%m/%d/%Y")

        # Get day item and add suffix
        day = c[2]
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        # Format into a readable format
        formatedDate = time.strftime("%A the %d" + suffix + " of %B, %Y", c)

        # Strip any leading zeros from the day
        formatedDate = formatedDate.replace(' 0', ' ')

        return formatedDate

###################################################################################################
@route(PREFIX + '/getteamname')
def getTeamName(teamName):
    # Display short or long team name

    useShortNames = Prefs["shortnames"]

    ShortTeams = Resource.Load(TEAM_NAMES, False)
    ShortTeams = JSON.ObjectFromString(ShortTeams)

    if useShortNames == "On":
        teamNameLower = teamName.lower()
        if teamNameLower in ShortTeams:
            return ShortTeams[teamNameLower] # It does so get name
        else:
            return teamName # It doesn't return original

    return teamName

###################################################################################################
@route(PREFIX + '/populatevideoarray', is_live = bool)
def populateVideoArray(videoArr, videoObj, is_live=False):
    game_id = videoObj['id']
    awayTeam = ''
    homeTeam = ''
    feedType = ''
    ligature = ''
    playingMarker = ''
    isPlaying = True
    summary = ''

    # Live stream specific

    if is_live:
        # If the game isn't on yet, set to gameoff vid
        if videoObj['isPlaying'] == 0:
             isPlaying = False

        if videoObj['isPlaying'] == 1: playingMarker = ">"

        # Populate summary with Start Time or current period (preferred)
        if videoObj['startTime']: summary = "Start Time: " + videoObj['startTime']
        if videoObj['period']: summary = videoObj['period']


    # On demand and Live stream


    # Set up home and away teams
    if videoObj['awayTeam']: awayTeam = videoObj['awayTeam']
    if videoObj['homeTeam']: homeTeam = videoObj['homeTeam']

    # Set up arena pic name (have to do it before 'vs' gets added)
    arena = R(ART)

    # Add 'vs' if there is a home and away team
    if homeTeam: ligature = ' @ '

    # Set up logo pic name
    logo = R(ICON)

    # Add playing indicator if game-on (maybe take this out)

    if videoObj['feedType']:
        if videoObj['feedType'] == "Away Feed":
            feedType = " - " + getTeamName(awayTeam) + " feed"
        elif videoObj['feedType'] == "Home Feed":
            feedType = " - " + getTeamName(homeTeam) + " feed"
        else:
            feedType = " - " + videoObj['feedType']

    # Built the title
    title = playingMarker + getTeamName(awayTeam) + ligature + getTeamName(homeTeam) + feedType

    if summary:
        summary = title + " - " + summary + " - Server: " + getServerLocation(False)
    else:
        summary = title + " - Server: " + getServerLocation(False)

    videoArr.append([game_id, title, logo, arena, summary, isPlaying])

###################################################################################################
@route(PREFIX + '/getserverlocation', prependQueryParam = bool)
def getServerLocation(prependQueryParam = True):
    serverLocation = Prefs["serverlocation"]

    if prependQueryParam == False: return serverLocation

    if (serverLocation == "Automatic"):
        return ""
    else:
        return "&location=" + String.Quote(serverLocation, True)
