import jwt
import random


jwt_api = "JC7aDtFZgpaD7K3MOXiI6tbPxlQBA9Lxto4Syg0g"


def get_special_key(query):
	alg = "HS512"

	text = {
		"api": query
	}
	result = jwt.encode(text, jwt_api, algorithm=alg)
	return str(random.randint(10000000, 99999999)) + ":" + str(result.split(".")[1][::-1])


def dictify_user(string):
	print(string, "DICTIFY")
	s = str(string).split(";")
	data = {
		"name": s[0],
		"surname": s[1],
		"position": s[2],
		"login date": str(s[3]),
		"email": s[4],
		"UID": s[5]
	}
	return data


def dictify_bot(string):
	s = str(string).split(";")
	data = {
		"telegram_id": s[0],
		"name": s[1],
		"status": s[2],
		"registered": s[3],
		"UID": s[4]
	}
	return data