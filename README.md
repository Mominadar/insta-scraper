# insta-scrapper
#PURPOSE OF PROGRAM

This program will scrape the names of all the accounts that the instagram page is following and find their most engaging post. Then the top most egaging posts of them are recorded in a google sheet which the client can access. It was done as a freelancing project for the client whose job was to fing the top 10 enagaging posts.

#STEPS TO USE PROGRAM

Download project file.

Open project directory and install all required modules. 

cd facebook-scrapper pip install dependeny-name

Go to setup/bot_settings.json to enter email and password of dummy account in relavent fields.


      "ACCOUNTS": [
                    "username:password"    #replace username with your dummy account name and password with account password. Do not remove colon.
                ],


    "TARGET_ACCOUNT": "" #the account whose followers are extracted

Generate key for using google sheets. Use this link: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

Copy client_secret.json file in data directory.

Add report link in line 220 in main.py. 

Run main.py. 

python facebook.py

After program finishes you canopen google sheet link to check results.
