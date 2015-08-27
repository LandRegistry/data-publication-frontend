Running the server:
mkvirtualenv -p /usr/bin/python3.4 data-publication-frontend
pip install -r requirements.txt
./run_flask_dev.sh

Accessing the system:
Chrome works best, but Firefox can also be used. IE is limited for local testing due to request header requirement.
For Chrome get the ModHeader plugin ("Modify Headers" or "HeaderTool" can be used with Firefox)
Add request header values for "iv-user" (e.g. sg1dp3000) and "iv-groups" (e.g. NSD)
Navigate to "http://127.0.0.1:5000/"
Enabling "iv-user" request header simulates user being logged in.
Enabling "iv-groups" with the relevant values enables access to content require those roles.
