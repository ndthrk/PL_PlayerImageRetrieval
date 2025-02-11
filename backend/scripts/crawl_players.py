import requests
import pandas as pd
import json
import os
from icrawler.builtin import GoogleImageCrawler
import shutil

# Đường dẫn đến file teams
FILE_TEAMS_PATH = "../../data/list_teams.json"
# Template URL để thu thập thông tin cầu thủ của đội
TEAM_INFO_URL_TEMPLATE = "https://footballapi.pulselive.com/football/teams/{}/compseasons/719/staff?pageSize=10&compSeasons=719"
# Thư mục lưu thông tin đội bóng
SAVE_DIR_PATH = "../../data/teams_info/"

def load_team_ids():
    """
    Đọc file JSON và lấy thông tin về id và tên các đội bóng.
    """
    with open(FILE_TEAMS_PATH, 'r') as file:
        data = json.load(file)
    
    teams_data = data.get("content", [])
    team_ids = [(team.get("name", "Unknown"), int(team.get("club", {}).get("id", -1))) for team in teams_data]
    
    return team_ids

def get_team_info(team_id):
    """
    Thu thập thông tin đội bóng từ URL.
    """
    url = TEAM_INFO_URL_TEMPLATE.format(team_id)
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}")
    return response.json()

def save_team_info(team_name, team_id, data):
    """
    Lưu thông tin đội bóng vào file JSON.
    """
    file_path = os.path.join(SAVE_DIR_PATH, f"{team_name}_{team_id}.json")
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
def crawl_teams_info():
    '''
    Thực hiện tất cả các bước thu thập thông tin cầu thủ
    '''
    teams = load_team_ids()
    for team_name, team_id in teams:
        print(f"{team_id} - {team_name}", end = ': ')
        
        team_info = get_team_info(team_id)
        if team_info:
            print("fetched - ", end = '')
            save_team_info(team_name, team_id, team_info)
            print("saved")
def get_data_players():
    '''
    Truy cập vào data đã lưu để lọc danh sách tên, id cầu thủ
    '''
    path = "../../data/teams_info"
    players_list = []  
    # Duyệt qua tất cả các file
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        name_team = data['team']['name']
        players = data['players']
        
        # print(name_team[:7], len(players), sep='\t')
        
        for player in players:
            players_list.append({'player_id': player['playerId'],
                                 'player_name':  player['name']['display'],
                                 'team': name_team})
    
    df = pd.DataFrame(players_list)
    print(f"{len(os.listdir(path))} clubs, Total: {df.shape[0]} players")
    return df

def crawl_image_icrawler(keyword, player_id, save_dir_img, n_images=6):
    """Tải ảnh từ Google Image bằng icrawler"""
    if not os.path.exists(save_dir_img):
        os.makedirs(save_dir_img)
    try:
        crawler = GoogleImageCrawler(storage={"root_dir": save_dir_img})
        crawler.crawl(keyword=keyword, max_num=n_images)
    except:
        print("Error",player_id)
    # Đổi tên file theo dạng {player_id}_stt
    for i, filename in enumerate(os.listdir(save_dir_img)):
        ext = filename.split(".")[-1]
        new_name = f"{player_id}_{i+1}.{ext}"
        os.rename(os.path.join(save_dir_img, filename), os.path.join(save_dir_img, new_name))
def crawl_raw_images():
    '''
    Thu thập ảnh từ google image
    '''
    df = get_data_players()

    for _, row in df.iterrows():
        key_word = f"{row['player_name']} {row['team']}"
        save_dir_img = f"../../data/raw_images/{row['player_id']}/"
        print(key_word)
        crawl_image_icrawler(key_word,row['player_id'],save_dir_img, n_images=5)
def check_data_img():
    """
    Kiểm tra dữ liệu ảnh. Nếu số lượng ảnh không đủ, xóa và tải lại.
    """
    path = "../../data/raw_images/"
    df_players = get_data_players()

    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        n_images = len(os.listdir(folder_path))

        player_info = df_players[df_players['player_id'] == int(folder)]
        if player_info.empty:
            print(f"Không tìm thấy thông tin ID: {folder}")
            continue
        player_name = player_info.iloc[0]['player_name']
        team_name = player_info.iloc[0]['team']
        
        # Nếu số lượng ảnh không đủ 5, xóa và tải lại
        if n_images != 5:
            print(f"{player_name} ({folder}), số lượng: {n_images}")

            # shutil.rmtree(folder_path)
            # os.makedirs(folder_path)

            # # Tải lại ảnh
            # keyword = f"{player_name} {team_name}"
            # crawl_image_icrawler(keyword, folder, folder_path, n_images=5)
if __name__ == "__main__":
    check_data_img()

'''
Danh sách data bị thiếu:
138551 77    Will Dennis 0
144961 348    Caoimhín Kelleher 1
160057 104    Christian Nørgaard 1
160724 358    Harvey Elliott 1
161345 414    Harry Maguire 1
258869 8    Thomas Partey 0
259014 574    Tomás Soucek 1
283726 298    Conor Chaplin 0
287700 292    Cameron Burgess 1
288967 71    Ryan Christie 0
325441 321    Wout Faes 1
328496 424    Kobbie Mainoo 1
335345 191    Harrison Murray-Campbell 1
337528 605    João Gomes 1
337950 270    Sasa Lukic 1
340568 543    Dejan Kulusevski 1
340956 143    Carl Rushworth 1
342476 412    André Onana 1
344967 277    Adama Traoré 1
346777 173    Cole Palmer 1
362856 308    Sam Szmodics 1
363095 309    Jens Cajuste 1
363304 149    Killian Cahill 1
363722 525    Aaron Ramsdale 1
364387 187    Jadon Sancho 1
41635 395    Phil Foden 1
47188 413    Victor Lindelöf 1
'''