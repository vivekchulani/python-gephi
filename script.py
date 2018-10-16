# Import sys for arguments, http client for api calls, json and time for request limitations to api
import sys
import http.client
import json
import time

# Base url the movie db
movie_base_url = "api.themoviedb.org"

# Arguments
if len(sys.argv) == 2:
	api_key = sys.argv[1]
else:
	print("You have not supplied the correct amount of arguments")

# Generic request
def sendRequest(url, api_key, params):
	connection = http.client.HTTPSConnection(movie_base_url)
	# Iterate over params dict
	param_string = ""
	for (key,value) in params.items():
		param_string += "&" + str(key) + "=" + str(value)
	#  Send request and return response
	connection.request("GET", url + "?api_key=" + api_key + param_string)
	response = connection.getresponse()
	return (response.read(), response.getheader("x-ratelimit-remaining"))

# b.
# Get genres to get comedy key value pair
params = {}
(genre_response, limit) = sendRequest("/3/genre/movie/list", api_key, params)
# Use json parser to grab comedy details
comedy_data = json.loads(genre_response)
for dict in comedy_data["genres"]:
	if dict["name"] == "Comedy":
		(comedy_id, comedy_name) = (dict["id"], dict["name"])

# Get 300 most popular movies in comedy genre released in the year 2000 or later. 
# Sort from most popular to least popular
movie_id_name_dict = {}
params = {}
for i in range(1,16):
	params["sort_by"] = "popularity.desc"
	params["page"] = i
	params["primary_release_date.gte"] = 2000
	params["with_genres"] = comedy_id
	(popular_movies_response, limit) = sendRequest("/3/discover/movie", api_key, params)
	pop_movie_data = json.loads(popular_movies_response)
	for dict in pop_movie_data["results"]:
		movie_id_name_dict[dict["id"]] = dict["original_title"]
# Write results to movie_ID_name.csv
f = open("movie_ID_name.csv", "w+")
for (identification, name) in movie_id_name_dict.items():
	f.write(str(identification)+","+name+"\n")
f.close()

# c.
# Get similar movies for each movie id above and store in dictionary
movie_id_sim_id_dict = {}
params = {}
for identification in movie_id_name_dict.keys():
	(similar_movies_response, limit) = sendRequest("/3/movie/"+str(identification)+"/similar", api_key, params)
	sim_movie_data = json.loads(similar_movies_response)
	if (limit == "0"):
		time.sleep(10)
	if "results" in sim_movie_data and len(sim_movie_data["results"]) > 0:
		sim_id_list = []
		for dict in sim_movie_data["results"][:5]:
			sim_id_list.append(dict["id"])
		movie_id_sim_id_dict[identification] = sorted(sim_id_list)
	else:
		continue

# Remove duplicate pairs
# Save the results in movie_ID_sim_movie_ID.csv
comparsion_list = [] # List of tuples for comparison
for (movie_id, similar_movie_ids) in sorted(movie_id_sim_id_dict.items()):
	for similar_movie_id in similar_movie_ids:
		if (similar_movie_id, movie_id) not in comparsion_list:
			movie_tuple = (movie_id, similar_movie_id)
			comparsion_list.append((movie_tuple))
f = open("movie_ID_sim_movie_ID.csv", "w+")
for (movie_id, similar_movie_id) in comparsion_list:			
	f.write(str(movie_id)+","+str(similar_movie_id)+"\n")
f.close()
