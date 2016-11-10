# Browserat
A POC reverse shell that can utilize multiple major web-browsers to provide remote access. Browserat is intended to demonstrate remote control of an endpoint within a high security network, if that endpoint is configured to use a web-proxy to access the internet, and is not restricted via a whitelist.

# Requirements
* Python Flask
* SQLAlchemy for Flask

# Details
Browserat is a quick-and-dirty demo of a reverse shell, capable of executing Windows OS commands and Powershell once the client is executed by a user on their endpoint. To achieve this, it performs the following actions:
1) On the affected machine, Browserat Client starts a local web-server on port 8899. This web-server is waiting for a POST parameter, c - once received in a request, this parameter is executed as an OS command, and the command's output is presented as a response.
2) On the affected machine, Browserat Client opens a browser (default is Firefox) with a URL for the command & control of the Browserat server as an argument.
3) The page returned by the Browserat server is a two-pronged CORS enabled web-page, which constantly polls the server for new commands and, once received, sends the new command to the localhost web-server for execution, obtains output from the response, and sends it back to the server.

# Execution
Server-side - Use "pip install -r requirements.txt" to obtain the relevant requirements. Then, simply execute Browserat.py until a BRAT> prompt is seen.
Client-side - edit the $controllerUrl parameter with your server's IP. Edit $browser_path to point at the browser you want to use (easy to implement a search and execute functionality here). If you want to run the browser in hidden mode, remove <##> from the <# -WindowStyle hidden #> flag.

# Caveats
This is hastily written POC code. It is intended to demonstrate basic command execution, and not much more. I don't intend to maintain, fix or add features to it, as I feel it serves its purpose as is.

# Assumptions
The assumptions we're working with here are:
* That a browser can be executed as "browser.exe [url]" to open a web-page. This applies to multiple major browsers - Chrome, Firefox, IE
* That the browser is preconfigured to use some sort of proxy, or can access the Browserat server
