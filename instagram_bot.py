from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time, os, traceback, requests, logging
import urllib.request
from utility_methods.utility_methods import *
from random import randint
from datetime import datetime

class InstaBot:
    def __init__(self, username=None, password=None):
        options = Options()
        options.headless = True
        self.username = config['IG_AUTH']['USERNAME']
        self.password = config['IG_AUTH']['PASSWORD']
        self.login_url = config['IG_URLS']['LOGIN']
        self.nav_user_url = config['IG_URLS']['NAV_USER']
        self.get_tag_url = config['IG_URLS']['SEARCH_TAGS']
        self.driver = webdriver.Firefox(options=options,executable_path=config['ENVIRONMENT']['FIREFOXDRIVER_PATH'])
        self.logged_in = False

    def waiting(self,a=2,b=6):
        _temp = randint(a,b)
        time.sleep(_temp)

    
    def login(self):
        self.driver.get(self.login_url)
        self.waiting(5,9)
        login_btn = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div') # login button xpath changes after text is entered, find first

        username_input = self.driver.find_element_by_name('username')
        password_input = self.driver.find_element_by_name('password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.waiting()
        login_btn.click()
        self.telegram_bot_sendtext('log in')
        self.waiting(4,7)


    
    def nav_user(self, user):
        """
        Navigates to a users profile page

        Args:
            user:str: Username of the user to navigate to the profile page of
        """

        self.driver.get(self.nav_user_url.format(user))
        self.waiting()
    

    
    def like_latest_posts(self, users,comments):
        error_counter = success_counter = 1
        last_user = None
        for user in users:
            self.nav_user(user)
            try:
                last_user = user
                url_post = self.driver.find_element_by_xpath('//div[@class="v1Nh3 kIKUG  _bz0w"]/a')
                #GRAP THE POST URL AND GO
                self.driver.get(url_post.get_attribute('href'))
                #like post
                self.like_post()
                self.comment_post(comments[randint(0,len(comments)-1)])
                #counting successfull processing
                success_counter += 1
                self.waiting(4,11)


            except Exception as e:
                last_user_index = users.index(user)

                updated_users_list = users[last_user_index+1:]
                with open(config['FILE_PATH']['FILE_PATH_LOCATION'],'w') as f:
                    f.writelines('')
                    for elem in updated_users_list:
                        f.writelines(str(elem)+'\n')
                #telegram notifier
                #msg = '[{0}] is private account or no posts yet detected'.format(user)
                #self.telegram_bot_sendtext(msg)

                #screenshoot
                now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S__")
                screenshoots_path = 'screenshoots/'+ now + str(user)+'.png'
                print(screenshoots_path)
                self.driver.save_screenshot(screenshoots_path)
                logging.warning(traceback.format_exc())
                logging.warning('failed-----------------------')
                #counting failed processing
                error_counter += 1

            finally:
                #counting all processing
                counter = error_counter + success_counter
                if counter % 2 == 0:
                    self.telegram_bot_sendtext('''
[{0:.1f}] in total
[{1:.1f}] succeded 
[{2:.1f}] failed
[{3:.1f} %] success rate
[{4:.1f} %] fail rate '''.format(counter,success_counter,error_counter,((success_counter/(success_counter+error_counter))*100),((error_counter/(success_counter+error_counter))*100)))

        self.telegram_bot_sendtext('all users have been processed')
        logging.info('all users have been processed')
        self.driver.close()
            


    
    def comment_post(self, text):
        """
        Comments on a post that is in modal form
        """
        self.waiting()
        self.driver.find_element_by_xpath('//textarea[contains(@class,"Ypffh")]').click()
        self.driver.find_element_by_xpath('//textarea[contains(@class,"Ypffh")]').send_keys(text,Keys.ENTER)

    def like_post(self):
        self.waiting(2,4)
        self.driver.find_element_by_xpath('//section[@class="ltpMr Slqrh"]/span[1]/button').click()

    def telegram_bot_sendtext(self,bot_message):
        bot_token = '1322367173:AAFdwlgfWPG8UnU8EbVrVuDFs1SUdMIGfbo'
        bot_chatID = '-453306470'
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()


if __name__ == '__main__':

    config_file_path = './config.ini' 
    logger_file_path = './bot.log'
    config = init_config(config_file_path)
    logger = get_logger(logger_file_path)

    #logging setup
    logging.basicConfig(filename='bot.log',
                            filemode='a+',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.WARNING)

    with open(config['FILE_PATH']['FILE_PATH_LOCATION']) as f:
        content = f.readlines()
    users = [x.strip() for x in content]

    comments = ['Collab ?dm @azarioo_off 🎁 ❤️',
                'Collab? dm @azarioo_off🎁❤️',
                'Collab ?dm @azarioo_off 🎁 ❤️',
                'Collab? dm @azarioo_off🎁 ❤️',
                'Collab with us? dm @azarioo_off 🎁❤️',
                'Collab? dm @azarioo_off 🎁 ❤️ 👍',
                'Collab ?dm @azarioo_off 🎁 👍 ❤️']

    bot = InstaBot()
    bot.login()
    bot.like_latest_posts(users,comments)