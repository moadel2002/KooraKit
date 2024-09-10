from flask import Flask, request, jsonify, send_file
import pandas as pd
from mplsoccer import Radar, FontManager, grid
import matplotlib.pyplot as plt
import io
import requests
from flask_cors import CORS
import cv2

app = Flask(__name__)
CORS(app)


URL1 = ('https://raw.githubusercontent.com/googlefonts/SourceSerifProGFVersion/main/fonts/'
        'SourceSerifPro-Regular.ttf')
serif_regular = FontManager(URL1)
URL2 = ('https://raw.githubusercontent.com/googlefonts/SourceSerifProGFVersion/main/fonts/'
        'SourceSerifPro-ExtraLight.ttf')
serif_extra_light = FontManager(URL2)
URL3 = ('https://raw.githubusercontent.com/google/fonts/main/ofl/rubikmonoone/'
        'RubikMonoOne-Regular.ttf')
rubik_regular = FontManager(URL3)
URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
robotto_thin = FontManager(URL4)
URL5 = ('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
        'RobotoSlab%5Bwght%5D.ttf')
robotto_bold = FontManager(URL5)



league_files = {
    "Premier League": "Datasets/ENG_Premier_League.csv",
    "La Liga": 'Datasets/ESP_La_Liga.csv',
    "Ligue 1": 'Datasets/FRA_Ligue1.csv',
    "Bundesliga": 'Datasets/GER_Bundesliga.csv',
    "Serie A": 'Datasets/ITA_Serie_A.csv'
}

teams_league_files = {
    "Premier League": "TeamDatasets/ENG_Premier_League.csv",
    "La Liga": 'TeamDatasets/ESP_La_Liga.csv',
    "Ligue 1": 'TeamDatasets/FRA_Ligue1.csv',
    "Bundesliga": 'TeamDatasets/GER_Bundesliga.csv',
    "Serie A": 'TeamDatasets/ITA_Serie_A.csv'
}

matrices = {
    "standard": ['Playing Time_MP', 'Playing Time_Starts', 'Playing Time_Min', 'Playing Time_90s', 'Performance_Gls', 'Performance_Ast', 'Performance_G+A', 'Performance_G-PK', 'Performance_PK', 'Performance_PKatt', 'Performance_CrdY', 'Performance_CrdR', 'Expected_xG', 'Expected_npxG', 'Expected_xAG', 'Expected_npxG+xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR'],
    "shooting": ['Standard_90s', 'Standard_Gls', 'Standard_Sh', 'Standard_SoT', 'Standard_SoT%', 'Standard_Sh/90', 'Standard_SoT/90', 'Standard_G/Sh', 'Standard_G/SoT', 'Standard_Dist', 'Standard_FK', 'Standard_PK', 'Standard_Katt', 'Expected_xG', 'Expected_npxG', 'Expected_npxG/Sh', 'Expected_G-xG', 'Expected_np:G-xG'],
    "passing": ['90s', 'Total_Cmp', 'Total_Att', 'Total_Cmp%', 'Total_TotDist', 'Total_PrgDist', 'Short_Cmp', 'Short_Att', 'Short_Cmp%', 'Medium_Cmp', 'Medium_Att', 'Medium_Cmp%', 'Long_Cmp', 'Long_Att', 'Long_Cmp%', 'Ast', 'xAG', 'Expected_xA', 'Expected_A-xAG', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP'],
    "passing_types": ['90s', 'Att', 'Pass Types_Live', 'Pass Types_Dead', 'Pass Types_FK', 'Pass Types_TB', 'Pass Types_Sw', 'Pass Types_Crs', 'Pass Types_TI', 'Pass Types_CK', 'Corner Kicks_In', 'Corner Kicks_Out', 'Corner Kicks_Str', 'Outcomes_Cmp', 'Outcomes_Off', 'Outcomes_Blocks'],
    "goal_shot_creation": ['90s', 'SCA', 'SCA90', 'SCA Types_PassLive', 'SCA Types_PassDead', 'SCA Types_TO', 'SCA Types_Sh', 'SCA Types_Fld', 'SCA Types_Def', 'GCA', 'GCA90', 'GCA Types_PassLive', 'GCA Types_PassDead', 'GCA Types_TO', 'GCA Types_Sh', 'GCA Types_Fld', 'GCA Types_Def'],
    "defense": ['90s', 'Tackles_Tkl', 'Tackles_TklW', 'Tackles_Def 3rd', 'Tackles_Mid 3rd', 'Tackles_Att 3rd', 'Challenges_Tkl', 'Challenges_Att', 'Challenges_Tkl%', 'Challenges_Lost', 'Blocks', 'Blocks_Sh', 'Blocks_Pass', 'Int', 'Tkl+Int', 'Clr', 'Err'],
    "possession": ['90s', 'Touches', 'Touches_Def Pen', 'Touches_Def 3rd', 'Touches_Mid 3rd', 'Touches_Att 3rd', 'Touches_Att Pen', 'Touches_Live', 'Take-Ons_Att', 'Take-Ons_Succ', 'Take-Ons_Succ%', 'Take-Ons_Tkld', 'Take-Ons_Tkld%', 'Carries', 'Carries_TotDist', 'Carries_PrgDist', 'Carries_PrgC', 'Carries_1/3', 'Carries_CPA', 'Carries_Mis', 'Carries_Dis', 'Receiving_Rec', 'Receiving_PrgR'],
    "playing_time": ['Starts', 'Starts_Mn/Start', 'Starts_Compl', 'Starts_Subs', 'Starts_Mn/Sub', 'Starts_unSub', 'Team Success_PPM', 'Team Success_onG', 'Team Success_onGA', 'Team Success_+/-', 'Team Success_+/-90', 'Team Success_On-Off', 'Team Success (xG)_onxG', 'Team Success (xG)_onxGA', 'Team Success (xG)_xG+/-', 'Team Success (xG)_xG+/-90', 'Team Success (xG)_On-Off'],
    "misc": ['90s', 'Performance_CrdY', 'Performance_CrdR', 'Performance_2CrdY', 'Performance_Fls', 'Performance_Fld', 'Performance_Off', 'Performance_Crs', 'Performance_Int', 'Performance_TklW', 'Performance_PKwon', 'Performance_PKcon', 'Performance_OG', 'Performance_Recov', 'Aerial Duels_Won', 'Aerial Duels_Lost', 'Aerial Duels_Won%']
}

teams_matrices = {
    "standard": ['Playing Time_MP', 'Playing Time_Starts', 'Playing Time_Min', 'Playing Time_90s', 'Performance_Gls', 'Performance_Ast', 'Performance_G+A', 'Performance_G-PK', 'Performance_PK', 'Performance_PKatt', 'Performance_CrdY', 'Performance_CrdR', 'Expected_xG', 'Expected_npxG', 'Expected_xAG', 'Expected_npxG+xAG', 'Progression_PrgC', 'Progression_PrgP'],
    "shooting": ['Standard_90s', 'Standard_Gls', 'Standard_Sh', 'Standard_SoT', 'Standard_SoT%', 'Standard_Sh/90', 'Standard_SoT/90', 'Standard_G/Sh', 'Standard_G/SoT', 'Standard_Dist', 'Standard_FK', 'Standard_PK', 'Expected_xG', 'Expected_npxG', 'Expected_npxG/Sh', 'Expected_G-xG', 'Expected_np:G-xG'],
    "passing": ['Total_Cmp', 'Total_Att', 'Total_Cmp%', 'Total_TotDist', 'Total_PrgDist', 'Short_Cmp', 'Short_Att', 'Short_Cmp%', 'Medium_Cmp', 'Medium_Att', 'Medium_Cmp%', 'Long_Cmp', 'Long_Att', 'Long_Cmp%', 'Ast', 'xAG', 'Expected_xA', 'Expected_A-xAG', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP'],
    "passing_types": ['Att', 'Pass Types_Live', 'Pass Types_Dead', 'Pass Types_FK', 'Pass Types_TB', 'Pass Types_Sw', 'Pass Types_Crs', 'Pass Types_TI', 'Pass Types_CK', 'Corner Kicks_In', 'Corner Kicks_Out', 'Corner Kicks_Str', 'Outcomes_Cmp', 'Outcomes_Off', 'Outcomes_Blocks'],
    "goal_shot_creation": ['SCA', 'SCA90', 'SCA Types_PassLive', 'SCA Types_PassDead', 'SCA Types_TO', 'SCA Types_Sh', 'SCA Types_Fld', 'SCA Types_Def', 'GCA', 'GCA90', 'GCA Types_PassLive', 'GCA Types_PassDead', 'GCA Types_TO', 'GCA Types_Sh', 'GCA Types_Fld', 'GCA Types_Def'],
    "defense": ['Tackles_Tkl', 'Tackles_TklW', 'Tackles_Def 3rd', 'Tackles_Mid 3rd', 'Tackles_Att 3rd', 'Challenges_Tkl', 'Challenges_Att', 'Challenges_Tkl%', 'Challenges_Lost', 'Blocks', 'Blocks_Sh', 'Blocks_Pass', 'Int', 'Tkl+Int', 'Clr', 'Err'],
    "possession": ['Touches', 'Touches_Def Pen', 'Touches_Def 3rd', 'Touches_Mid 3rd', 'Touches_Att 3rd', 'Touches_Att Pen', 'Touches_Live', 'Take-Ons_Att', 'Take-Ons_Succ', 'Take-Ons_Succ%', 'Take-Ons_Tkld', 'Take-Ons_Tkld%', 'Carries', 'Carries_TotDist', 'Carries_PrgDist', 'Carries_PrgC', 'Carries_1/3', 'Carries_CPA', 'Carries_Mis', 'Carries_Dis', 'Receiving_Rec', 'Receiving_PrgR'],
    "playing_time": ['Starts', 'Starts_Mn/Start', 'Starts_Compl', 'Starts_Subs', 'Starts_Mn/Sub', 'Starts_unSub', 'Team Success_PPM', 'Team Success_onG', 'Team Success_onGA', 'Team Success_+/-', 'Team Success_+/-90', 'Team Success (xG)_onxG', 'Team Success (xG)_onxGA', 'Team Success (xG)_xG+/-', 'Team Success (xG)_xG+/-90'],
    "misc": ['Performance_CrdY', 'Performance_CrdR', 'Performance_2CrdY', 'Performance_Fls', 'Performance_Fld', 'Performance_Off', 'Performance_Crs', 'Performance_Int', 'Performance_TklW', 'Performance_PKwon', 'Performance_PKcon', 'Performance_OG', 'Performance_Recov', 'Aerial Duels_Won', 'Aerial Duels_Lost', 'Aerial Duels_Won%']
  }

def load_league_data(league):
    if league in league_files:
        file_path = league_files[league]
        df = pd.read_csv(file_path)
        return df
    else:
        return None
    
def load_teams_league_data(league):
    if league in teams_league_files:
        file_path = teams_league_files[league]
        df = pd.read_csv(file_path)
        return df
    else:
        return None

@app.route('/leagues', methods=['GET'])
def get_leagues():
    return jsonify(list(league_files.keys()))

@app.route('/seasons', methods=['GET'])
def get_seasons():
    league = request.args.get('league')
    isPlayer = request.args.get("isPlayer")

    if isPlayer == "true":
        df = load_league_data(league)
        if df is not None:
            seasons = df['season'].unique().tolist()
            return jsonify(seasons)
        else:
            return jsonify([])
    else:
        df = load_teams_league_data(league)
        if df is not None:
            seasons = df['season'].unique().tolist()
            return jsonify(seasons)
        else:
            return jsonify([])

@app.route('/teams', methods=['GET'])
def get_teams():
    league = request.args.get('league')
    season = int(request.args.get('season'))

    isPlayer = request.args.get("isPlayer")

    if isPlayer == "true":
        df = load_league_data(league)
        if df is not None:
            seasons = df['season'].unique().tolist()
        else:
            return jsonify([])
    else:
        df = load_teams_league_data(league)
        if df is not None:
            seasons = df['season'].unique().tolist()
        else:
            return jsonify([])
        
    if df is not None:
        teams = df[df['season'] == season]['team'].unique().tolist()
        return jsonify(teams)
    else:
        return jsonify([])

@app.route('/players', methods=['GET'])
def get_players():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    team = request.args.get('team')
    df = load_league_data(league)
    if df is not None:
        players = df[(df['season'] == season) & (df['team'] == team)]['player'].unique().tolist()
        return jsonify(players)
    else:
        return jsonify([])

@app.route('/teamsRadar', methods=['GET'])
def create_radar_chart():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    team = request.args.get('team')
    event = request.args.get('event')

    df = load_teams_league_data(league)
    event_columns = teams_matrices[event]
    team_data = df[(df['season'] == season) & (df['team'] == team)][event_columns]
    numeric_columns = team_data.select_dtypes(include='number').columns
    max_values = df[numeric_columns].max()
    min_values = df[numeric_columns].min()

    params = numeric_columns.tolist()
    team_values = team_data.iloc[-1][numeric_columns].tolist()

    radar = Radar(params, min_values, max_values, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)

    fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025, title_space=0, endnote_space=0, grid_key='radar', axis=False)

    radar.setup_axis(ax=axs['radar'])

    rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
    radar_output = radar.draw_radar(team_values, ax=axs['radar'], kwargs_radar={'facecolor': '#aa65b2'}, kwargs_rings={'facecolor': '#66d8ba'})
    radar_poly, rings_outer, vertices = radar_output

    range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=15, zorder=2.5)
    param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=15)
    lines = radar.spoke(ax=axs['radar'], color='#a6a4a1', linestyle='--', zorder=2)

    axs['title'].text(0.5, 0.5, f'{team} ({league})', ha='center', va='center', fontsize=20)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    
    return send_file(img, mimetype='image/png')

def drop_first_dict_entry(data):
    # Iterate through each key in the outer dictionary
    for column_name in data:
        # Get the inner dictionary for the current column
        inner_dict = data[column_name]
        # Check if the inner dictionary has at least one item
        if inner_dict:
            # Drop the first item from the inner dictionary
            first_key = next(iter(inner_dict))
            data[column_name] = data[column_name][first_key]
            
    return data


def get_player_info():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    team = request.args.get('team')
    player = request.args.get('player')
    event = request.args.get('event')

    df = load_league_data(league)
    if df is not None:
        player_data = df[(df['season'] == season) & (df['team'] == team) & (df['player'] == player)]
        player_data = drop_first_dict_entry(player_data.to_dict())
        print(player_data)
    
    return player_data

player_report = "\nTitle: Dejan Kulusevski's Season Performance Analysis: A Comprehensive Review of Tottenham's Versatile Prodigy\n\nIntroduction:\n\nDejan Kulusevski, the young and dynamic forward for Tottenham, has had an impressive season in the 2022 ENG-Premier League. With a blend of attacking prowess, defensive acumen, and technical skills, Kulusevski has emerged as a key player for Tottenham. This report delves into his performance statistics, highlighting his strengths, weaknesses, and notable contributions throughout the season.\n\nShooting:\n\nKulusevski's goal-scoring ability has been a significant asset for Tottenham this season. With 5 goals in 26 shots, he boasts a shooting percentage of 34.6%, demonstrating his efficiency in front of the goal. Although he has not scored from free kicks or penalties, his 9 shots on target showcase his ability to find the back of the net when presented with opportunities.\n\nPassing:\n\nKulusevski's passing statistics reveal his well-rounded technical abilities and his role as a creative force in Tottenham's attacking play. With 404 completed passes out of 486 attempts, he has a completion percentage of 83.1%, indicating his accuracy and precision in distributing the ball. His 259 completed short passes and 8 assists demonstrate his ability to create scoring opportunities for his teammates.\n\nKulusevski's passing types showcase his versatility and adaptability in different game situations. He has made 3 free kick passes, 7 through balls, and 25 crosses, indicating his ability to contribute to the team's attacking play from various positions on the field.\n\nDefense:\n\nKulusevski's defensive contributions have been equally impressive, as evidenced by his statistics. With 19 tackles and 13 successful tackles won, he has shown his ability to disrupt the opposition's attacking play. His 14 blocks and 13 interceptions further highlight his defensive capabilities, while his 38 miscontrols and 15 fouls drawn indicate his willingness to engage in the physical aspects of the game.\n\nPossession:\n\nKulusevski's possession statistics demonstrate his ability to control the game and dictate play. With 643 touches and 643 live-ball touches, he has been a constant presence in the midfield, contributing to Tottenham's possession-based style of play. His 25 take-ons and 19 take-ons won showcase his ability to penetrate the opposition's defense, while his 449 passes received indicate his role as a key link between Tottenham's midfield and attack.\n\nMiscellaneous:\n\nKulusevski's disciplinary record has been commendable, with only 3 yellow cards and no red cards throughout the season. His 20 fouls committed and 15 fouls drawn indicate his willingness to engage in the physical aspects of the game, while his 4 offsides and 25 crosses highlight his occasional lapses in positioning.\n\nNotable Contributions:\n\nThroughout the season, Kulusevski has made several notable contributions to Tottenham's success. His goal-scoring ability has been crucial in securing vital victories, while his creative passing and defensive contributions have helped Tottenham maintain a solid defensive record.\n\nConclusion:\n\nDejan Kulusevski's performance in the 2022 ENG-Premier League season has been nothing short of impressive. His goal-scoring ability, combined with his technical skills, creative passing, and defensive contributions, have made him a vital player for Tottenham. While there is room for improvement in certain areas, such as his occasional positioning and fouls committed, Kulusevski's overall impact on the team has been significant. As he continues to develop and refine his skills, it is clear that he will remain a key player for Tottenham in the years to come."

@app.route('/playerReport', methods=['GET'])
def get_player_report():
    url = "https://1700-01j1056tzpjxkdk3j84q1t7t0n.cloudspaces.litng.ai/generate_playerr_report"
    data = get_player_info()
    response = requests.post(url=url, json=data)

    try:
        json_response = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response")
    print(json_response['report'])
    return json_response['report']


def get_team_info():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    team = request.args.get('team')
    event = request.args.get('event')
    df = load_teams_league_data(league)
    if df is not None:
        team_data = df[(df['season'] == season) & (df['team'] == team)]
        team_data = drop_first_dict_entry(team_data.to_dict())
        print(team_data)
    
    return team_data

team_report = "\n\nTitle: Arsenal's 2021 Premier League Season: A Comprehensive Analysis of Performance and Tactical Approach\n\nIntroduction:\n\nThe 2021 Premier League season witnessed Arsenal's relentless pursuit of excellence, as they strived to reclaim their position among the elite clubs in English football. With a total of 53 goals scored, 38 assists, and a commendable defensive record, Arsenal showcased a well-rounded performance throughout the season. This report delves into the team's tactical approach, key players, and significant matches, providing a comprehensive analysis of their overall performance.\n\nTactical Approach:\n\nArsenal's tactical approach during the 2021 season was characterized by a balanced emphasis on both offensive and defensive aspects. The team's possession-based style of play was evident, with an average of 25,431 touches and 25,425 live-ball touches, reflecting their commitment to maintaining control of the game. The team's 18,041 completed passes and 21,807 pass attempts highlighted their focus on maintaining possession and creating opportunities through intricate passing sequences.\n\nOffensively, Arsenal's 53 goals and 38 assists demonstrated their ability to create and convert scoring opportunities. The team's 47 non-penalty goals and 23 free-kick shots showcased their versatility in finding the back of the net. The average shot distance of 17.7 meters indicated the team's ability to penetrate the opposition's defense with precision and power.\n\nDefensively, Arsenal's 456 tackles, 252 tackles won, and 351 interceptions reflected their commitment to regaining possession and disrupting the opposition's attacking flow. The team's 643 clearances and 368 blocks demonstrated their ability to thwart shots and maintain a solid defensive structure.\n\nKey Players:\n\nSeveral key players contributed significantly to Arsenal's performance during the 2021 season. Alexandre Lacazette, the team's leading scorer with 19 goals, showcased his prowess in front of goal, while Pierre-Emerick Aubameyang provided crucial assists and goal-scoring opportunities. Granit Xhaka's impressive 10 assists and 10 shots on target highlighted his importance in the team's attacking play.\n\nDefensively, David Luiz and Gabriel Magalh\u00e3es played pivotal roles in the team's defensive efforts, with Luiz's 10 tackles won and Magalh\u00e3es' 10 blocks contributing to the team's solid defensive record.\n\nSignificant Matches and Turning Points:\n\nArsenal's 2021 season was marked by several significant matches and turning points that influenced their standing in the league. The team's 3-0 victory over Manchester City at the Emirates Stadium in April 2021 was a crucial win that helped them climb up the table and maintain their position in the top four.\n\nAnother notable match was the 2-1 victory over Liverpool at Anfield in September 2021, which showcased Arsenal's ability to compete against the league's top teams. The match was a turning point for the team, as it demonstrated their resilience and ability to challenge the league's elite.\n\nConclusion:\n\nArsenal's 2021 Premier League season was a testament to their commitment to a balanced and effective tactical approach. The team's offensive and defensive performances, combined with the contributions of key players, helped them maintain a competitive position in the league. While the season had its ups and downs, Arsenal's overall performance showcased their potential to challenge for a top-four finish in the future. As the team looks ahead to the next season, they will undoubtedly build upon the lessons learned and continue to strive for excellence in the Premier League."


@app.route('/teamReport', methods=['GET'])
def get_team_report():
    url = "https://1700-01j1056tzpjxkdk3j84q1t7t0n.cloudspaces.litng.ai/generate_team_report"
    data = get_team_info()
    response = requests.post(url=url, json=data)

    try:
        json_response = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response")
    print(json_response['report'])
    return json_response['report']




@app.route('/playerRadar', methods=['GET'])
def get_radar():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    team = request.args.get('team')
    player = request.args.get('player')
    event = request.args.get('event')
    
    df = load_league_data(league)
    if df is not None:
        event_columns = matrices[event]
        player_data = df[(df['season'] == season) & (df['team'] == team) & (df['player'] == player)][event_columns]
        if not player_data.empty:
            player_data = player_data.iloc[:, :8]
            numeric_columns = player_data.select_dtypes(include='number').columns
            max_values = df[numeric_columns].max()
            min_values = df[numeric_columns].min()

            params = numeric_columns.tolist()
            player_values = player_data.iloc[-1][numeric_columns].tolist()

            radar = Radar(params, min_values, max_values, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)

            fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025, title_space=0, endnote_space=0, grid_key='radar', axis=False)

            radar.setup_axis(ax=axs['radar'])
            rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
            radar_output = radar.draw_radar(player_values, ax=axs['radar'], kwargs_radar={'facecolor': '#aa65b2'}, kwargs_rings={'facecolor': '#66d8ba'})
            radar_poly, rings_outer, vertices = radar_output

            range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=15, zorder=2.5)
            param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=15)
            lines = radar.spoke(ax=axs['radar'], color='#a6a4a1', linestyle='--', zorder=2)

            axs['title'].text(0.5, 0.5, f'{player} - {team} ({league})', ha='center', va='center', fontsize=20)

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plt.close(fig)
            
            return send_file(img, mimetype='image/png')
    return jsonify({"error": "Player data not found"}), 404

@app.route('/twoPlayersRadar', methods=['GET'])
def get_radar_two_players():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    season2 = int(request.args.get('season2'))
    team1 = request.args.get('team')
    player1 = request.args.get('player')
    team2 = request.args.get('team2')
    player2 = request.args.get('player2')
    event = request.args.get('event')

    df = load_league_data(league)
    if df is not None:
        event_columns = matrices[event]
        player1_data = df[(df['season'] == season) & (df['team'] == team1) & (df['player'] == player1)][event_columns]
        player2_data = df[(df['season'] == season2) & (df['team'] == team2) & (df['player'] == player2)][event_columns]


        if not player1_data.empty and not player2_data.empty:


            player1_data = player1_data.iloc[:, :8]
            player2_data = player2_data.iloc[:, :8]
            
            numeric_columns = player1_data.select_dtypes(include='number').columns
            max_values = df[numeric_columns].max()
            min_values = df[numeric_columns].min()

            params = numeric_columns.tolist()
            player1_values = player1_data.iloc[-1][numeric_columns].tolist()
            player2_values = player2_data.iloc[-1][numeric_columns].tolist()

            # radar = Radar(params, min_values, max_values, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)

            # fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025, title_space=0, endnote_space=0, grid_key='radar', axis=False)

            # radar.setup_axis(ax=axs['radar'])
            # rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
            # radar_output1 = radar.draw_radar(player1_values, ax=axs['radar'], kwargs_radar={'facecolor': '#aa65b2'}, kwargs_rings={'facecolor': '#66d8ba'})
            # radar_output2 = radar.draw_radar(player2_values, ax=axs['radar'], kwargs_radar={'facecolor': '#fc5f5f'}, kwargs_rings={'facecolor': '#fc5f5f'})
            # radar_poly1, rings_outer1, vertices1 = radar_output1
            # radar_poly2, rings_outer2, vertices2 = radar_output2

            # range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=15, zorder=2.5)
            # param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=15)
            # lines = radar.spoke(ax=axs['radar'], color='#a6a4a1', linestyle='--', zorder=2)

            # axs['title'].text(0.5, 0.5, f'{player1} ({team1}) vs {player2} ({team2}) - {league}', ha='center', va='center', fontsize=20)
            radar = Radar(params, min_values, max_values, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)


            # creating the figure using the grid function from mplsoccer:
            fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                            title_space=0, endnote_space=0, grid_key='radar', axis=False)



            # plot radar
            radar.setup_axis(ax=axs['radar'])  # format axis as a radar
            rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
            radar_output = radar.draw_radar_compare(player1_values, player2_values, ax=axs['radar'],
                                                    kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
                                                    kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
            radar_poly, radar_poly2, vertices1, vertices2 = radar_output

            range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=25,
                                                fontproperties=robotto_thin.prop)

            param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=25,
                                                fontproperties=robotto_thin.prop)

            axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1],
                                c='#00f2c1', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)
            axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1],
                                c='#d80499', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)

            # adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
            # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)

            title1_text = axs['title'].text(0.01, 0.65, player1, fontsize=25, color='#01c49d',
                                            fontproperties=robotto_bold.prop, ha='left', va='center')
            title2_text = axs['title'].text(0.01, 0.25, season, fontsize=20,
                                        fontproperties=robotto_thin.prop,
                                        ha='left', va='center', color='#01c49d')

            title3_text = axs['title'].text(0.99, 0.65, player2, fontsize=25,
                                            fontproperties=robotto_bold.prop,
                                            ha='right', va='center', color='#d80499')

            title4_text = axs['title'].text(0.99, 0.25, season2, fontsize=20,
                                            fontproperties=robotto_thin.prop,
                                            ha='right', va='center', color='#d80499')
            img = io.BytesIO()
            fig.savefig(img, format='png', dpi=300)
            img.seek(0)
            plt.close(fig)

            return send_file(img, mimetype='image/png')
        
    return "Player data not found", 404


@app.route('/twoTeamsRadar', methods=['GET'])
def get_radar_two_teams():
    league = request.args.get('league')
    season = int(request.args.get('season'))
    season2 = int(request.args.get('season2'))
    team1 = request.args.get('team')
    team2 = request.args.get('team2')
    event = request.args.get('event')

    df = load_league_data(league)
    if df is not None:
        event_columns = teams_matrices[event]
        team1_data = df[(df['season'] == season) & (df['team'] == team1)][event_columns]
        team2_data = df[(df['season'] == season2) & (df['team'] == team2)][event_columns]

        if not team1_data.empty and not team2_data.empty:


            team1_data = team1_data.iloc[:, :12]
            team2_data = team2_data.iloc[:, :12]
            
            numeric_columns = team1_data.select_dtypes(include='number').columns
            max_values = df[numeric_columns].max()
            min_values = df[numeric_columns].min()

            params = numeric_columns.tolist()
            team1_values = team1_data.iloc[-1][numeric_columns].tolist()
            team2_values = team2_data.iloc[-1][numeric_columns].tolist()

            # radar = Radar(params, min_values, max_values, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)

            # fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025, title_space=0, endnote_space=0, grid_key='radar', axis=False)

            # radar.setup_axis(ax=axs['radar'])
            # rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
            # radar_output1 = radar.draw_radar(team1_values, ax=axs['radar'], kwargs_radar={'facecolor': '#aa65b2'}, kwargs_rings={'facecolor': '#66d8ba'})
            # radar_output2 = radar.draw_radar(team2_values, ax=axs['radar'], kwargs_radar={'facecolor': '#fc5f5f'}, kwargs_rings={'facecolor': '#fc5f5f'})
            # radar_poly1, rings_outer1, vertices1 = radar_output1
            # radar_poly2, rings_outer2, vertices2 = radar_output2

            # range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=15, zorder=2.5)
            # param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=15)
            # lines = radar.spoke(ax=axs['radar'], color='#a6a4a1', linestyle='--', zorder=2)

            # axs['title'].text(0.5, 0.5, f'({team1}) vs ({team2}) - {league}', ha='center', va='center', fontsize=20)
            radar = Radar(params, min_values, max_values, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)


            # creating the figure using the grid function from mplsoccer:
            fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                            title_space=0, endnote_space=0, grid_key='radar', axis=False)



            # plot radar
            radar.setup_axis(ax=axs['radar'])  # format axis as a radar
            rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
            radar_output = radar.draw_radar_compare(team1_values, team2_values, ax=axs['radar'],
                                                    kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
                                                    kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
            radar_poly, radar_poly2, vertices1, vertices2 = radar_output

            range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=25,
                                                fontproperties=robotto_thin.prop)

            param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=25,
                                                fontproperties=robotto_thin.prop)

            axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1],
                                c='#00f2c1', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)
            axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1],
                                c='#d80499', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)

            # adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)

            title1_text = axs['title'].text(0.01, 0.65, team1, fontsize=25, color='#01c49d',
                                            fontproperties=robotto_bold.prop, ha='left', va='center')
            title2_text = axs['title'].text(0.01, 0.25, season, fontsize=20,
                                        fontproperties=robotto_thin.prop,
                                        ha='left', va='center', color='#01c49d')

            title3_text = axs['title'].text(0.99, 0.65, team2, fontsize=25,
                                            fontproperties=robotto_bold.prop,
                                            ha='right', va='center', color='#d80499')

            title4_text = axs['title'].text(0.99, 0.25, season2, fontsize=20,
                                            fontproperties=robotto_thin.prop,
                                            ha='right', va='center', color='#d80499')

            img = io.BytesIO()
            fig.savefig(img, format='png', dpi=300)
            img.seek(0)
            plt.close(fig)

            return send_file(img, mimetype='image/png')
    return "Team data not found", 404


from all.system import imageflow_demo, transfer_playerpoints_to_plane, transfer_ballpoints_to_plane, cae_with_kmeans, assign_teams, distanceandspeed, getall

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    

@app.route('/upload', methods=['POST'])
def upload_video():
    file = request.files['video']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    cap = cv2.VideoCapture(filename)
    frames = []
    i = 1
    while(cap.isOpened()):
        ret,frame = cap.read()
        if ret == True:
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            frames.append(frame)
        else:
            break
        
    playerresults,ballresults,homography,trackbboxes = imageflow_demo(frames[:1],1080,1920,30)
    transformed_player_points = transfer_playerpoints_to_plane(playerresults,homography)
    transformed_ball_points = transfer_ballpoints_to_plane(homography,ballresults)
    kmeans = cae_with_kmeans(transformed_player_points,trackbboxes)
    teams = assign_teams(kmeans,trackbboxes,playerresults,transformed_player_points)
    alldistanceandspeed = distanceandspeed(transformed_player_points,25,5)
    alldata = getall(alldistanceandspeed,teams,transformed_player_points)
    return alldata


if __name__ == '__main__':
    app.run(debug=True)
