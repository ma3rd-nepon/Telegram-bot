import jwt
import random


jwt_api = "JC7aDtFZgpaD7K3MOXiI6tbPxlQBA9Lxto4Syg0g"


def get_special_key(query):
	alg = "HS512"

	text = {
		"api": query
	}
	result = jwt.encode(text, jwt_api, algorithm=alg)
	return str(result.split(".")[1][::-1])