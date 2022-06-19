from genericpath import exists
from linecache import cache
import requests
import json
import os
import urllib
from bs4 import BeautifulSoup
import time
import ast

"""applies color on terminal"""
class colors:
    orange = '\033[33m'
    grey = '\033[90m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    magenta = '\033[95m'
    cyan = '\033[96m'
    white = '\033[97m'
    default = '\033[0m'
    purple = '\033[35m'

'''scraper base functions'''
class Input_Converter:
    '''converts any data into json formatt'''
    @staticmethod
    def raw_to_json(filename,data):
        conv_data = json.dumps(data)
        with open(filename,'w') as file:
            file.write(conv_data)
    
    '''input query validation'''
    @staticmethod
    def data_extractor(query):
        if not isinstance(query,str):
            raise TypeError
        encoded_url = urllib.parse.quote(query)
        return encoded_url
    
    '''html filter'''
    @staticmethod
    def html_remover(text):
        cleantext = BeautifulSoup(text,'lxml').text
        return cleantext
    
    '''cache saver'''
    @staticmethod
    def cache(text):
        print(text)
        with open('scraper_state.txt','w') as file:
            file.write(text)
     
    '''cache remover'''
    def cache_remover(self):
        try:
            os.remove('scraper_state.txt')
        except:
            pass
    
    '''reading cache files'''
    def file_reader(filename):
        response = None
        with open(filename,'rt',encoding='UTF-8') as file:
            response= file.readline()
        return response
            



class Scrapper:
    def __init__(self):
        self.search = None
        self.input_conv = Input_Converter()
        self.prev = None
        self.next = None
        self.total = 0

    '''annapurna website crawler'''
    def data_getter(self, search_value,execute_further = False):
        try:

            url = None

            if execute_further:
                url =f'https://bg.annapurnapost.com{search_value}'
            else:
                encoded_url = self.input_conv.data_extractor(search_value)
                url = f'https://bg.annapurnapost.com/api/search?title={encoded_url}'
            print(url)
            res= requests.get(url).json()
            # print(res)
            response_keys = res.keys()
            if "error" in response_keys:
                return 'Sorry your search query has no data Exiting The program--->'
                
            main_data = res['data']
            res_data = main_data['items']
            if len(res_data) < 1:
                return 'Sorry your search query has no data Exiting The program--->'
            all_link = main_data['links']
            ret_data = []
            try:
                self.prev = all_link.get('prev',None)
                self.next = all_link.get('next', None)
                self.total= main_data.get('total',0)
            except:
                pass

            '''saving cache state'''
            try:
                if self.next != None:
                    print(f'{colors.purple}saving cahce state--->{colors.default}')
                    new_obj = {'next_url':self.next}
                    self.input_conv.cache(str(new_obj))
            except:
                pass

            
            for data in res_data:
                data['content'] = self.input_conv.html_remover(data['content'])
                ret_data.append(data)
            return ret_data

        except:
            return 'Sorry an error ocurred on the program. Exiting The program--->'
        
    def prev_next_func(self):
            '''while loop intiated for prev and next featur'''
            while self.prev != None or self.next != None:
                time.sleep(2)
                print('')
                print(f'{colors.yellow} ####Executing the scipt for previous and next data###')
                print('')
                time.sleep(2)
                new_response = None

                inp_val = input(f'''{colors.green} 
                In order to extract wither previous or next data please use "prev" for extracting previous data or use "next" for extracting the remaining data: ''')
                
                '''input length validation'''
                if len(inp_val) < 1:
                    raise AttributeError  

                '''input validation'''
                if inp_val != 'prev' and inp_val != 'next':
                    print(f'{colors.red}Please insert either prev or next as input value.Exiting the program #####{colors.default}')
                    break
                
                if inp_val == 'prev':
                    if self.prev == None:
                        print(f'{colors.red}Sorry no previous data to loadExiting the program #####{colors.default}')
                        break

                    '''executing previous scraper'''
                    new_response = self.data_getter(self.prev,True)
                    
                if inp_val == 'next':
                    if  self.next == None:
                        print(f'{colors.red}Sorry no other data to load.Exiting the program #####{colors.default}')
                        break

                    '''executing next scraper'''
                    new_response = self.data_getter(self.next,True)

                
                print(new_response)
    
    def cache_rem(self):
        #removing cahce as the program exists:
            try:
                print(f'{colors.purple}clearing scraper caches{colors.default}')
                self.input_conv.cache_remover()
            except:
                pass

    def search_func(self,**kwargs):
        try:
            search_value=kwargs.get('search',None)
            cache_status = False
            if search_value is None:
                search_value = input(f'{colors.green} Welcome to annapurna post scraper. Please input a value to search {colors.default}: ')
                if len(search_value) < 1:
                    raise AttributeError
            else:
                cache_status = True
                          
            response = self.data_getter(search_value,cache_status)
            print(response)
            
            '''intialting prev _next func'''
            self.prev_next_func()
            self.cache_rem()

            


        except  AttributeError:
            print(f'{colors.red}Note:  One or more characters should be provided as the input {colors.default}')  

        except Exception as e:
            print(e)

def main():
    class_intiator = Scrapper()
    cache_checker = os.path.exists('scraper_state.txt')
    if cache_checker is not True:
        class_intiator.search_func()
    else:
        file_reader = Input_Converter.file_reader('scraper_state.txt')
        conv_obj = ast.literal_eval(file_reader)['next_url']
        # res = class_intiator.data_getter(conv_obj,True)
        # print(res)
        class_intiator.search_func(search=conv_obj)

        
    print(cache_checker)
if __name__ == '__main__':
   main()

