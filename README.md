# Sevak

Utility to scrape professor research areas and find their H index from Google Scholar.

## To Install
 
 * Clone the repo locally : ` git clone https://github.com/iit-technology-ambit/Sevak.git `
* `cd Sevak`
* Spawn a pipenv shell inside his folder : `pipenv shell`
If pipenv isn't installed, run `pip3 install python-pipenv` and then `pipenv shell`
* To install dependencies `pipenv install `

## To Run

* Create a client_secret.json file on the Google Developers Console. Make sure you add the Google Drive API. Visit the link for more instructions: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
* Sevak supports passing a list of departments for which you want the list as an argument. 
For example, if you want results only for Mechanical, CS and Civil Engineering, you can run the app as `python app.py CE CS ME`
* To run Sevak for all departments, just run `python app.py`
* To start the process, open `localhost:5000` in your browser and let it run. It takes about 4 hours for Sevak to run completely. 

