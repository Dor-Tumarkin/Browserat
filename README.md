# Browserat
A POC reverse shell that can utilize multiple major web-browsers to provide remote access. Browserat is intended to demonstrate remote control of an endpoint within a high security network, if that endpoint is configured to use a web-proxy to access the internet, and is not restricted via a whitelist.

# Requirements
* Python Flask
* SQLAlchemy for Flask

# Details
Browserat is a quick-and-dirty demo of a reverse shell, capable of executing Windows OS commands and Powershell once the client is executed by a user on their endpoint, by using the user's own browser as a pivot to connect the client with its server. To achieve this, it performs the following actions:
1) On the affected machine, Browserat Client starts a local web-server on port 8899. This web-server is waiting for a POST parameter, c - once received in a request, this parameter is executed as an OS command, and the command's output is presented as a response.
2) On the affected machine, Browserat Client opens a browser (default is Firefox) with a URL for the command & control of the Browserat server as an argument.
3) The page returned by the Browserat server is a two-pronged CORS enabled web-page, which constantly polls the server for new commands and, once received, sends the new command to the localhost web-server for execution, obtains output from the response, and sends it back to the server.

# Setup
* Server-side - Use "pip install -r requirements.txt" to obtain the relevant requirements. Then, simply execute Browserat.py until a BRAT> prompt is seen.
* Client-side - edit the $controllerUrl parameter with your server's IP. Edit $browser_path to point at the browser you want to use (easy to implement a search and execute functionality here). If you want to run the browser in hidden mode, remove <##> from the <# -WindowStyle hidden #> flag. You will receive no prompts of a successful connection, so simply type "BRAT> dir" to verify it works.

# Caveats
This is hastily written POC code. It is intended to demonstrate basic command execution, and not much more. I don't intend to maintain, fix or add features to it, as I feel it serves its purpose as is. Running it is likely to leave you exposed, so use responsibly.
Also, this is not the original POC. It has been rewritten to be a lot less messy, but consequently was not as widely tested. The original POC was proven to work across Windows 7, 8, 10 and Chrome, Interent Explorer, Firefox; this version PROBABLY shouldn't be any different.

# Features
Browserat saves all outputs to a SQLite DB in the form of a history. You can access the history from the BRAT> CLI. It's all in the help blob. Browserat runs in a "cmd /c" Powershell context; by starting a statement with a semi-colon (;), you can easily escape it to execute regular Powershell syntax.

# Assumptions
The assumptions we're working with here are:
* That the Browserat client is executed by a victim on their system, via social engineering or other form of infection
* That a browser can be executed as "[browser executable] [url arg]" to open a web-page. This applies to multiple major browsers - Chrome, Firefox, IE
* That the victim browser can access the Browserat server, either directly or via a web-proxy

# Acks
Thanks to Oren Ofer and Roy Haroush for helping with the concept and testing on the original POC.
