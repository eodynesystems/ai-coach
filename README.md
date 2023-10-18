# Coach

## How to update messages? 
1. Clone this repository
2. Download the [messages google sheet](https://docs.google.com/spreadsheets/d/1bfoWjKYeqvl6D2GbQr-37MGudZka1qNuIaS2nVedbGQ/edit#gid=0) as csv and save it in the root directory as `messages.csv`
3. Navigate to the messages directory and run the `update_messages.py` script
4. Commit the modified messages to the repo and pull the changes in the server for the changes to take effect in the app.

#### The google sheet must have the following formatting: 
- The first column must be called "Use Case" with no trailing white spaces
- Message columns must be named as "v1_Spanish", v2_Ukrainian etc.