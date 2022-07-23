# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 09:34:33 2022

@author: Roberto

Download survey data from KoboToolbox.
"""

import requests
import os


class Kobo():
    
    def __init__(self, token: str):
        self.token = token
        self.assets = self.get_all_assets()
        self.surveys = self.get_surveys_positions()


    def get_all_assets(self):
        '''
        Retrieve all assets linked to your user.
        
        '''
        assets = []
        url = None
        while True:
            new_assets = self.get_assets(url)
            assets.extend(new_assets["results"])
            url = new_assets["next"]
            if url is None:
                break
                
        print("Expected assets:", new_assets["count"])
        print("Downloaded assets:", len(assets))
        if new_assets["count"] == len(assets):
            print("OK")
        else:
            print("WARNING: Could not retrieve the expected number of assets.")
        return assets


    def get_assets(self, url: str = None):
        '''
        Retrieve assets according to a specific URL.
        
        '''
        if url is None:
            url = "https://kf.kobotoolbox.org/api/v2/assets.json"
        self.headers = {'Authorization': f'Token {token}'}
        print("Contacting:", url)
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    
    def get_surveys_positions(self):
        '''
        Retrieve all indices in self.assets that correspond to a survey.
        '''
        return [i for i, asset in enumerate (self.assets) \
                if asset["asset_type"]=="survey"]
    
    
    
    def save_all_surveys(self):
        '''
        Save to disk all surveys, both as csv and xlsx.
        
        '''
        for survey in self.surveys:
            self.save_asset(survey)
            self.save_asset(survey, savetype="xlsx")
    
    
    def save_asset(self, assetno: int, savetype: str = "csv"):
        '''
        General method to save an asset to disk.
        `assetno` is the index of the asset in `self.assets`.
        
        '''
        if savetype not in ["csv", "xlsx"]:
            print("savetype must be 'csv' or 'xlsx'.")
        else:
            url = self.assets[assetno]["export_settings"][0]["data_url_"+savetype]
            res = requests.get(url, headers = self.headers)
            if res.ok:
                filename = self.assets[assetno]["uid"]+"_"+self.assets[assetno]["name"]+"."+savetype
                filename = sanitize_for_windows(filename)
                filename = os.path.join("data", filename)
                print("Saving:", filename)
                with open(filename, "wb") as f:
                    f.write(res.content)
            else:
                print("Unable to retrieve the url: ", url)
                
    
    def save_uid(self, uid: str, savetype: str = "csv"):
        '''
        Save to disk an asset by its uid.
        
        '''
        assetno = None
        for i, asset in enumerate(self.assets):
            if asset["uid"] == uid:
                assetno = i
        
        if assetno is not None:
            self.save_asset(assetno, savetype)
        else:
            print("UID not found.")
                

def sanitize_for_windows(filename: str, forbidden: str = '\\/:*?"<>|'):
    '''
    Sanitize a filename removing forbidden characters.
    
    '''
    return "".join([[x, "_"][x in forbidden] for x in filename])
    


if __name__ == "__main__":
    if "token.txt" not in os.listdir():
        print("Could not find the `token.txt` file.")
    else:
        with open("token.txt", "r") as f:
            token = f.read().strip()
            data = Kobo(token)
            data.save_all_surveys()

