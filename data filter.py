#Magali Ngouabou 
import argparse
import logging
import os
import time
import json
import collections 

import requests
import openpyxl
import json
from stscraper import github
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from stutils import decorators as d


import stutils

# IMPORTANT: do this before creation of the first API object
stutils.CONFIG['GITHUB_API_TOKENS'] = [token1, token2, token3]

input_file = (input_file)
output_file  = (output_file)
user_emails = dict()
#tokens from 3 different accounts because 
#GitHub limits queries to 5000 per hour
#So with 3 tokens, you can get up to 15000 queries
#per hours
api = github.GitHubAPIv4(tokens = [token1, token2, token3])


'''
define a variable as json output
say that var is called json
it is like a dictionary with keys and values
e.g. json['email']
'''
QUERY = """
    query ($user: String!) {
    user(login: $user) {
      login
      name
      company
      email
  
      
  }
}

"""

                    
def check_for_email(user):
    '''
    send the query to check if user has an email listed
    maybe also check if they have a website listed
    (as emails could be hidden there)
    store or write email into the excel sheet
    else write 'email not listed'
    '''
    sleep_timer = 1
    
    while True: 
        
        
        try:
            # send the query
            gen = api.v4(QUERY, user=user)
            # result of the query
            query_result = next(gen)            
            #print(gen)
        except:
            #print("Profile not found")
            return None
        
        if "message" in query_result:
            # put some time between queries
            # so server isn't bombarded
            time.sleep(sleep_timer)
            sleep_timer *= 2
            # stop on the 8th hit
            if sleep_timer >= 256:
                return
            #otherwise, continue
            continue
        
        return query_result

def verify_email(query_result):
    '''
    outputs a string representing
    the desired results found from the query
    '''
    # if the query yields nothing, leave it alone
    if query_result == None:
        print("Nothing found")
        return None
    
    # when email not in the data
    if "data" not in query_result:
        print("Data not listed")
        return None
    
    
    # double check user exists; null = None json -> python
    if query_result['data']['user'] == None:
        contact = "User not found"
        return contact
    
    #if email not found, check for website
    if not query_result['data']['user']['email']:
        contact = "No email info listed"

        return contact 
        
    else:
    #else store that email 
        contact = query_result['data']['user']['email'] 
    #print(email)
    return contact

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Record user email")
    parser.add_argument("-i", "--input",
                        default="npm_infox.xlsx", 
                        type=argparse.FileType('r'),
                        help="Input excel filename."
                        "The file has a 'login' column")
    parser.add_argument("-v", "--verbose", 
                        action="store_true",
                        help="Log progress")
    args = parser.parse_args()
    
    #change the default configs for logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO if args.verbose else logging.WARNING)
    
    dataframe = pd.read_excel(input_file)
    # list of users gathered from excel login column
    users = dataframe['login']
    #open existing workbook
    wb = openpyxl.load_workbook(output_file) 
    #ws = wb.active 
    ws = wb.active
    i = 0
    for user in users:
        
        user = str(user)
        logging.info(user)
        user_emails[user] = verify_email(check_for_email(user))
        ws.cell(row=i+2, column=6).value = user_emails[user]
        i += 1
        if user_emails[user] == None:
            continue
        
    #save your work!    
    wb.save(output_file)
    
    