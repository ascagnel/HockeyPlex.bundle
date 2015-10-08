HockeyPlex
========
Plex plugin for [hockeystreams.com](http://www4.hockeystreams.com/assist/categories/13/api+discussion/4814/APP+HockeyPlex)
Adapting project from kevcenteno (https://github.com/kevcenteno/BallPlex.bundle)

Original author @ version 0.3:  FredenFromSweden
Original author @ BallPlex: kevcenteno
## Installation
You need to install Plex Media Server before you can use this plugin.

**If you have a previous version of hockeyPlex, please remove it before installing an updated version**

1. Download the latest version of hockeyPlex [here](https://github.com/kevcenteno/hockeyPlex.bundle/archive/master.zip)
2. Extract the `hockeyPlex.bundle-master` folder from the zip file and rename this folder to `hockeyPlex.bundle`
3. Move the `hockeyPlex.bundle` folder from step 3 into the Plex Media Server, Plug-ins folder:
  * Mac: `~/Library/Application Support/Plex Media Server/Plug-ins/`
  * Windows: `C:\Users\<your user>\AppData\Local\Plex Media Server\Plug-ins`
  * Linux: `(Installation Directory)/Application Support/Plex Media Server/Plug-ins/`
4. Restart Plex Media Server

### Configure
Most devices will allow you to enter your hockeyStreams username and password from the Log In menu when you go to the hockeyPlex Channel. If your device does not, you can enter them using the Plex Media Manager. To do this:

1. Choose Media Manager from the Plex menu in your menubar/taskbar or open the Plex Media Server app again.
2. Under Channels, choose hockeyPlex.
3. Click the "Settings" (gear) icon.
4. Enter your hockeystreams account username and password, press "Save" to save

### REMEMBER
1. You must setup your Plex Media Server to use the port 32400 and open that port on your router.
2. If you want to see Live Streams on Plex Web Client, you must use a full HTML5 browser (Example: Microsoft Edge), or you can disable flash on your browser (Example: Chrome´s Pepperflash)

## Known Issues
* Live streams don't work on Xbox 360. This is due to the incompatibility of the Plex Xbox 360 app and HLS streams. Plex developers are working on it, I notified the bug ;-).

## This app has been tested using a Windows 10 server and Windows 10, Android, Chromecast and Xbox 360 clients, all systems worked live and on-demand streams (except Xbox 360´s Plex App live streams.)
