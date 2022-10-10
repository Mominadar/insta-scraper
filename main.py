import os,sys,time,json,multiprocessing
from instabot import Bot
from datetime import datetime,timedelta,date
import uuid,gspread,requests
from oauth2client.service_account import ServiceAccountCredentials
from tqdm import tqdm
from operator import itemgetter

##############################################################################################################################
####################################################### FILES PATH ###############################################################
##############################################################################################################################
##############################################################################################################################


configurations = os.path.join(os.getcwd(),'settings.json')
agent = {'User-agent':"Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"}


##############################################################################################################################
####################################################### BOT.PY ###############################################################
##############################################################################################################################
##############################################################################################################################

def countdown(t):
    print("[+] SLEEP FOR '{}' SECONDS".format(t))
    time.sleep(t)
    print("")

def get_user_following_count(username):
    try:
        url = 'https://www.instagram.com/' + username
        r = requests.get(url).text

        start = '"edge_followed_by":{"count":'
        end = '},"followed_by_viewer"'
        # followers= r[r.find(start)+len(start):r.rfind(end)]

        start = '"edge_follow":{"count":'
        end = '},"follows_viewer"'
        followings = int(r[r.find(start)+len(start):r.rfind(end)])
    except:
        followings = 158
    return followings

def read_following_file(user_following_file_path):
    followings = []
    try:
        file = open(user_following_file_path,'r')
        for line in file.readlines():
            try:
                if not line.strip():continue
                followings.append(line.strip())
            except:pass
    except:
        open(user_following_file_path,'w').close()
    return followings

class MY_BOT():
    
    def __init__(
                    self,username, password, 
                    TARGET_ACCOUNT,
                    base_path
                ):
        self.username = username
        self.password = password
        self.TARGET_ACCOUNT = TARGET_ACCOUNT
        self.top_posts = []
        self.is_login = False
        self.my_bot = Bot(base_path=base_path)
    
    def login(self):
        if self.is_login:
            return
        print("\n[++] Trying to login with username '{}' ".format(self.username))
        res = self.my_bot.login(username=self.username,password=self.password,ask_for_code=True)
        if res:
            print("[{}] Login successfully !\n".format(self.username))
            self.is_login = True
        else:
            print("[{}] Login Failed !\n[!!] Check Username/password then try again.\n".format(self.username))
            while 1:pass

    def logout(self):
        if not self.is_login:
            return
        print('\n[{}] Hey! I am Logout for a small Moment (just get ridding of detection stuff) :)'.format(self.username))
        self.my_bot.logout()
        self.is_login = False

    #######    GETTERS  #######

    def get_user_id(self,user):
        try:
            res = requests.get("https://www.instagram.com/{}?__a=1".format(user))
            data = res.text
            data = json.loads(data)
            ID = data.get('graphql').get('user').get('id')
        except:
            ID = '38777285461'
        return ID

    def get_username_from_id(self,user_id):
        global agent
        url = "https://i.instagram.com/api/v1/users/{}/info/".format(user_id)
        res = requests.get(url,headers=agent)
        try:
            data = res.json()
            username = data.get('user').get("username")
            time.sleep(2)
            return username
        except:
            return None

    def get_user_followings(self,target_username_id,target_username):
        user_following_file_path = os.path.join(os.getcwd(),'data','core',target_username.replace("@",'').replace(".",'')+"_followings.txt")
        followings = []
        new_following_count = get_user_following_count(target_username)
        try:
            file = open(user_following_file_path,'r')
            for line in file.readlines():
                try:
                    if not line.strip():continue
                    followings.append(line.strip())
                except:pass
        except:
            open(user_following_file_path,'w').close()
        if new_following_count > len(followings):
            print("[+] Fetching Following List From Api....")
            followings = self.my_bot.get_user_following(target_username_id)
        else:
            print("[+] Fetching Following List From local file....")

        file = open(user_following_file_path,'w')
        for foll in followings:
            file.write(str(foll)+"\n")
        file.close()

        return followings

    def get_last_week_medias(self,name):
        POSTS = []
        url = "https://www.instagram.com/{}/?__a=1".format(name)
        date_before_7_days = (datetime.now() - timedelta(7)).date()
        res = requests.get(url)
        try:
            data = res.json()
            posts = data.get('graphql').get('user').get('edge_owner_to_timeline_media').get('edges')
            for post_data in posts:
                post_data = post_data.get('node')
                shortcode = post_data.get('shortcode')
                total_followers = data.get('graphql').get('user').get('edge_followed_by').get('count')
                post_date = datetime.fromtimestamp(post_data.get('taken_at_timestamp')).date()
                if post_date < date_before_7_days:
                    continue
                POSTS.append({
                        'post_link':"https://www.instagram.com/p/"+shortcode,
                        'total_likes':post_data.get("edge_liked_by").get('count'),
                        'total_comments':post_data.get('edge_media_to_comment').get('count'),
                        'owner_username':name,
                        'total_followers':total_followers
                    })
        except Exception as e:
            print(e)
        return POSTS
    
    def get_top_post(self,posts):
        top_post = {
                        'post_link':posts[0].get('post_link'),
                        'total_likes':posts[0].get('total_likes'),
                        'total_comments':posts[0].get('total_comments'),
                        'likes_plus_comments':posts[0].get('total_likes')+posts[0].get('total_comments'),
                        'owner_username':posts[0].get('owner_username'),
                        'profile_link':"https://www.instagram.com/"+posts[0].get('owner_username'),
                        'total_followers':posts[0].get('total_followers')

                    }
        for post in posts:
            likes_plus_comments = post.get('total_likes') + post.get('total_comments')
            if likes_plus_comments > top_post['likes_plus_comments']:
                top_post = {
                    'post_link':post.get('post_link'),
                    'total_likes':post.get('total_likes'),
                    'total_comments':post.get('total_comments'),
                    'likes_plus_comments':likes_plus_comments,
                    'owner_username':post.get('owner_username'),
                    'profile_link':"https://www.instagram.com/"+post.get('owner_username'),
                    'total_followers':post.get('total_followers')
                }
        return top_post

    #######    REPORT GEN  #######

    def report_generate(self,top_posts):
        print("\n\n[+] Generating Report ...... ")
        CLIENT_SECRET_FILE = os.path.join(os.getcwd(), "data", "client_secret.json")
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Report").sheet1
        sheet.update_cell(1, 1, "Username")
        sheet.update_cell(1, 2, "Profile_link")
        sheet.update_cell(1, 4, "Engagement rate")
        sheet.update_cell(1, 5, "Post_link")
        sheet.update_cell(1, 6, "Likes")
        sheet.update_cell(1, 7, "Comments")
        pbar = tqdm(total=len(top_posts))
        for i in range(1,len(top_posts)):
            sheet.update_cell(i+1,1,top_posts[i]['owner_username'])
            sheet.update_cell(i+1,2,top_posts[i]['profile_link'])
            sheet.update_cell(i+1,3,top_posts[i]['total_followers'])
            sheet.update_cell(i+1,4,top_posts[i]['likes_plus_comments'])
            sheet.update_cell(i+1,5,top_posts[i]['post_link'])
            sheet.update_cell(i+1,6,top_posts[i]['total_likes'])
            sheet.update_cell(i+1,7,top_posts[i]['total_comments'])
            pbar.update(n=1)
        pbar.close()
        print('[->] Google sheet Updated Successfully !')
        print("[->] You can access google sheet at: ")
        print("\n[Link] -> https://docs.google.com/spreadsheets/d/1V3_VTL6FP1I4RgevB_EUtiy5aO075HjjfUQv0piVtVg/edit?usp=sharing")
        print("\n\n")

    #######    BOT DRIVER  #######

    def bot_driver(self):

        v_new_followings_count = get_user_following_count(self.TARGET_ACCOUNT)
        following_count_in_file = len(read_following_file(os.path.join(os.getcwd(),'data','core',self.TARGET_ACCOUNT.replace("@",'').replace(".",'')+"_followings.txt")))
        if v_new_followings_count > following_count_in_file:
            self.login()
        else:
            print("[+] Continue Without Login....")

        # calcualte current account target chunk
        ID = self.get_user_id(self.TARGET_ACCOUNT)
        target_user_followings_list = self.get_user_followings(ID,self.TARGET_ACCOUNT)

        ALL_TOP_POSTS = []

        number = 1
        for following in target_user_followings_list:
            followee_username = self.get_username_from_id(following)
            print('\n[{}] Current Followee -> "{}"'.format(number,followee_username))
            posts = self.get_last_week_medias(followee_username)
            if not posts:
                print("[+] No Last Week Post Found.....")
            else:
                top_post_data = self.get_top_post(posts)
                ALL_TOP_POSTS.append(top_post_data)
                print("[+] Found a Top Post.")

            number += 1

            if number % 20 == 0:
                countdown(30)

        ALL_TOP_POSTS.sort(key=itemgetter('likes_plus_comments'),reverse=True)
        
        ALL_TOP_POSTS = ALL_TOP_POSTS[:10]

        self.report_generate(ALL_TOP_POSTS)


            

##############################################################################################################################
####################################################### RUNNER.PY ############################################################
##############################################################################################################################


def runner(username,password,TARGET_ACCOUNT):

    base_path = os.path.join(os.getcwd(),'logs',username.replace('@','').replace('.','')+"_logs")
    if not os.path.exists(base_path):
        os.mkdir(base_path)
        os.mkdir(os.path.join(base_path,'log'))

    ### initialize
    BOT = MY_BOT(
                    username, password, 
                    TARGET_ACCOUNT,
                    base_path
                )

    # ### driver bot
    BOT.bot_driver()

def main():
    # read data from configuration file
    accounts,TARGET_ACCOUNT = read_configuration_Data()
    username,password = accounts[0].split(":")
    runner(username,password,TARGET_ACCOUNT)

##############################################################################################################################
####################################################### MAIN.PY ##############################################################
##############################################################################################################################

def read_configuration_Data(fileName = configurations):
    try:
        f = open (fileName,'r')
    except:
        f = open (fileName,'w')
        f.close()
        print("[--] File {} Not Located. Creating new file, edit it and try again".format(fileName))
        time.sleep(15)
        sys.exit()

    data = json.load(f)
    try:
        return data['ACCOUNTS'],data['TARGET_ACCOUNT']
    except Exception as e:
        print(e)
        print("[++] WRONG INPUT DATA IN 'input.json'.. Correct it and try again.")
        time.sleep(15)
        exit(1)

def check_and_make():
    if not os.path.exists(os.path.join(os.getcwd(),'data','core')):
        os.mkdir(os.path.join(os.getcwd(),'data','core'))
    if not os.path.exists(os.path.join(os.getcwd(),'config')):
        os.mkdir(os.path.join(os.getcwd(),'config'))
    if not os.path.exists(os.path.join(os.getcwd(),'logs')):
        os.mkdir(os.path.join(os.getcwd(),'logs'))

if __name__ == "__main__":
    check_and_make()
    main()
    while 1:pass


