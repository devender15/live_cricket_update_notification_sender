import requests
from bs4 import BeautifulSoup
from plyer import notification
import time
from win32com.client import Dispatch


def get_website(url):
	r = requests.get(url)
	return r.text

def notify_me(title, message):
	notification.notify(
		title = title,
		message = message,
		timeout = 10
	)

def speak(str):
	speak = Dispatch("SAPI.SpVoice")
	speak.Speak(str)


def select_match():
	home_page = get_website("https://www.espncricinfo.com/live-cricket-score")

	soup = BeautifulSoup(home_page, "html.parser")

	match_links = []
	match_names = []

	for all_matches in soup.find("div", class_="no-gutters").find_all("a", limit=2, class_="match-info-link-FIXTURES"):
		match_links.append(all_matches['href'])

	# getting all the match names
	first_match = soup.find("div").find_all("span", class_="category")[5]
	match_names.append(first_match.get_text())


	second_match = soup.find_all("div", class_="col-md-8")[1].find("div").find_all("span", class_="category")[5]
	match_names.append(second_match.get_text())

	complete_data = dict(zip(match_names, match_links))

	return complete_data

def score_checker(url):
	data = get_website(url)

	soup = BeautifulSoup(data, "html.parser")

	# info about current match
	status_red = soup.find("div", class_="match-info-MATCH").find("div", class_="description")

	# latest event i.e 4, 6 or Wicket
	latest_event = soup.find("div", class_="match-comment-run")
	# print(latest_event.get_text())


	team_one = soup.find("div", class_="match-info-MATCH").find("div", class_="teams").find("div", class_="name-detail").find("a").find("p")

	team_two = soup.find("div", class_="match-info-MATCH").find("div", class_="teams").find_all("div", class_="team")[1].find("div", class_="name-detail").find("a").find("p")

	score_batting_one = soup.find("div", class_="match-info-MATCH").find("div", class_="teams").find("div", class_="score-detail")

	score_batting_two = soup.find("div", class_="match-info-MATCH").find("div", class_="teams").find_all("div", class_="team")[1].find("div", class_="score-detail")


	# getting over completed value
	try:	
		over = soup.find("div", class_="match-comment-run-col")
		over_parsed = over.get_text().split(".")
		current_over = over_parsed[0]

	except Exception as not_started:
		pass


	# formatting the batting team score with name

	try:
		bat1 = f"{team_one.get_text()}  :   {score_batting_one.get_text()}"
		bat2 = f"{team_two.get_text()}  :   {score_batting_two.get_text()}"
		# print(bat2)
		pass
	except Exception as e:
		# print(f"{team_two.get_text()} is bowling! ")
		bat1 = "  "
		bat2 = "  "

	status_text = soup.find("div", class_="match-info-MATCH").find("div", class_="status-text")

	try:	
		return latest_event.get_text(), bat1, bat2, status_text.get_text(), current_over, status_red.get_text()

	except Exception as q:
		# print(f"error: {q}")
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


	if(user_input==1):

		if(score_checker("https://www.espncricinfo.com" + link_1)==None):
			print("Match is not LIVE, please come later.")

		else:
			event, score, score2, status_text_, current_over_, info_match = score_checker("https://www.espncricinfo.com" + link_1)


			print("\nMatch updating has been started...\n\n ")
			print(info_match)

			while(True):
				event, score, score2, status_text_, current_over_, info_match = score_checker("https://www.espncricinfo.com" + link_1)

				# checking for 4, 6 or Wicket from latest event
				if(event=="4"):
					four = "4!  Its a FOUR ! "
					speak("FOUR Runs !")
					notify_me(four, f"{score}\n{score2}\n{status_text_}")
					time.sleep(40)

				elif(event=="6"):
					six = "6!  Boom!  SIX !"
					speak("Maximum! Its a SIX !")
					notify_me(six, f"{score}\n{score2}\n{status_text_}")
					time.sleep(40)

				elif(event=="W"):
					wicket = "Wicket! He got him"
					speak("Out! Bowler got his wicket!")
					notify_me(wicket, f"{score}\n{score2}\n{status_text_}")
					time.sleep(80)

			print("Match is Ended !")

	elif(_input==2):

		if(score_checker("https://www.espncricinfo.com" + link_2)==None):
			print("Match is not LIVE, please come later.")

		else:
			event, score, score2, status_text_, current_over_, info_match = score_checker("https://www.espncricinfo.com" + link_2)


			print("Now Fourth Umpire is active, just listen to the updates and do your other work :) ")
			print(info_match)

			while(True):
				event, score, score2, status_text_, current_over_, info_match = score_checker("https://www.espncricinfo.com" + link_2)

				# checking for 4, 6 or Wicket from latest event
				if(event=="4"):
					four = "4!  Its a FOUR ! "
					speak("FOUR Runs !")
					notify_me(four, f"{score}\n{score2}\n{status_text_}")
					time.sleep(40)

				elif(event=="6"):
					six = "6!  Boom! Its a SIX !"
					speak("Maximum! Its a SIX !")
					notify_me(six, f"{score}\n{score2}\n{status_text_}")
					time.sleep(40)

				elif(event=="W"):
					wicket = "Wicket! He got him"
					speak("Out! Bowler got his wicket!")
					notify_me(wicket, f"{score}\n{score2}\n{status_text_}")
					time.sleep(80)

			print("Match is Ended !")

	else:
		print("Please select an appropriate option !")

if __name__ == '__main__':

	choice = select_match()
	print("Top two matches are :\n")

	for live in choice:
		print(live)

	_input = int(input("\nSelect any match you want to get update:\n"))

	start_updating(_input)
