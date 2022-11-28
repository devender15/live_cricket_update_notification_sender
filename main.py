import requests
from bs4 import BeautifulSoup
from lxml import etree, html
from discord_webhook import DiscordWebhook, DiscordEmbed


def send_discord(title, text, color):
    WH_URL = "https://discord.com/api/webhooks/934155161469861958/9m_Sdcvxwb-kCAkYFTLDtbe79BSPawq3L6CqYnB-J0uq3hadqUeVEaX0zYlMx3m2owlC"

    wh = DiscordWebhook(url=WH_URL)
    embed = DiscordEmbed(title=title, description=text, color=color)
    wh.add_embed(embed=embed)
    wh.execute()

# send_discord("wicket", "he got him!")


def get_website(url):
    r = requests.get(url)
    return r.text


def select_match():
    home_page = get_website("https://www.espncricinfo.com/live-cricket-score")

    soup = BeautifulSoup(home_page, "html.parser")

    match_links = []  # this array will store the match links
    match_names = []

    for all_matches in soup.findAll("a", class_="ds-no-tap-higlight"):
        # print(all_matches.get_text())
        match_links.append(all_matches.get("href"))

    # getting all the match names

    for i in range(len(soup.find_all("span", class_="ds-underline"))):
        match_name = soup.find_all("span", class_="ds-underline")[i]
        # print(match_name.get_text())
        match_names.append(match_name.get_text())

    # print(match_names)

    complete_data = dict(zip(match_names, match_links))
    # print(complete_data)
    return complete_data


def score_checker(url):
    data = get_website(url)

    soup = BeautifulSoup(data, "html.parser")

    tree = html.fromstring(data)

    # info about current match
    unnecessory_keywords = ["Match State: Innings Break"]

    event_array = tree.xpath(f'//*[@id="{url}"]//text()')

    # removing the non-required elements from the array because we only want overs and "W", "6" or "4" events.
    for line in unnecessory_keywords:
        if (line in event_array):
            event_array.remove(line)

    print(event_array)
    # latest event i.e 4, 6 or Wicket
    latest_event = event_array[1]
    print(latest_event)

    team_one = soup.findAll("div", class_="ci-team-score")[-2]  # team1 score
    team_two = soup.findAll("div", class_="ci-team-score")[-1]  # team2 score

    current_over = ""
    over_val = ""

    # getting the value completed after the over
    try:
        over = soup.find("div", class_="match-comment-run-col")
        over_parsed = over.get_text().split(".")
        current_over = over_parsed[0]
        over_val = over.get_text()[:-1]

    except Exception as not_started:
        pass

    # formatting the batting team score with name

    try:
        bat1 = team_one.get_text()
        bat2 = team_two.get_text()

    except Exception as e:
        # print(f"{team_two.get_text()} is bowling! ")
        bat1 = "  "
        bat2 = "  "

    # status_text = soup.find("div", class_="match-info-MATCH-full-width").find("div", class_="status-text")

    try:
        return latest_event, bat1, bat2, current_over, over_val

    except Exception as q:
        print(f"error: {q}")
        return None


def start_updating(user_input):

    choice = select_match()

    # converting all keys of dictionary to a list
    key_list = list(choice.keys())
    match_1 = key_list[0]
    match_2 = key_list[1]

    # getting all respective links
    link_1 = choice[match_1]
    link_2 = choice[match_2]

    if (user_input == 1):

        if (score_checker("https://www.espncricinfo.com" + link_1) == None):
            print("Match is not LIVE, please come later.")

        else:
            event, score, score2, current_over_, over_val = score_checker(
                "https://www.espncricinfo.com" + link_1)

            print(
                "Now Fourth Umpire is active, just listen to the updates and do your other work :) ")

            # making this check for not repeating same notification again and again !
            check = {}

            while (True):
                event, score, score2, current_over_,  over_val = score_checker(
                    "https://www.espncricinfo.com" + link_1)

                # checking for 4, 6 or Wicket from latest event
                if (event == "4"):
                    if (over_val not in check):
                        check[over_val] = True
                        four = "4!  Its a FOUR ! "
                        send_discord(four, f"{score}\n{score2}\n", "FFA500")

                elif (event == "6"):
                    if (over_val not in check):
                        check[over_val] = True
                        six = "6!  Boom!  SIX !"
                        send_discord(six, f"{score}\n{score2}\n", "00FF00")

                elif (event == "W"):
                    if (over_val not in check):
                        print("wicket")
                        check[over_val] = True
                        wicket = "Wicket! He got him"
                        send_discord(wicket, f"{score}\n{score2}\n", "FF0000")

                else:
                    pass

            print("Match is Ended !")

    else:
        print("Please select an appropriate option !")


if __name__ == '__main__':

    choice = select_match()
    print("Available LIVE matches :\n")

    for live in choice:
        print(live)

    _input = int(input("\nSelect any match you want to get update:\n"))

    start_updating(_input)
