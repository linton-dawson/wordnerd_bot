#Twitter Bot - @wordnerd_bot
#Created by :- Pushkar, Shrunkhala, Prathamesh, Sakshi (March 2020)

import requests
import json
import tweepy
import time

#OAuth handler for token authentication
auth = tweepy.OAuthHandler('cpJv6ggRa36AbBv7y34oOMNVc','QJ1PvbkvuOhRFkff1xA9Uh3UPu8sE4M8qlw6QjNFbDimrI1Mzj')
auth.set_access_token('2995257804-nML6wjPnCo5am5TlbVbsi2fGulIIVN4280dipCl','FzeN99RJWi40XDv4zfbMuzQywLnhj4AW88UsrtAkCMR7O')



#Function which checks tweets and gives reply to query tweet
def mentioned_reply(keywords,prev_id) :
	init_id = prev_id
	api = tweepy.API(auth,wait_on_rate_limit = True)
	print('Rate limit not crossed. Proceeding to get un-replied mentions... ')

	#Using Twitter API cursoring through tweepy to paginate large results
	for twt in tweepy.Cursor(api.mentions_timeline, since_id = prev_id).items() :
	
		#Get id of recent tweet
		init_id = max(twt.id, init_id)
		#Checks if the tweet is a reply or a timeline tweet
		if twt.in_reply_to_status_id is not None :
			continue
		
		#Favorites the tweet
		if not twt.favorited :
			api.create_favorite(twt.id)

			#Checks for certain keywords so as to not reply to unqueried tweeets
			if any(keyword in twt.text.lower() for keyword in keywords) :
				the_tweet = processTweet(twt.text.lower(), twt.user.screen_name)
				if not twt.user.following :
					twt.user.follow() 
	
				#Updates status
				try:
					api.update_status(
					status = the_tweet,
					in_reply_to_status_id = twt.id,
					)
				except :
					api.destroy_favorite(twt.id)
					break
	
				print('Status has been updated. Please check the reply to tweet !')
		else :
			continue

	return init_id



#Function that deals with Datamus API calls and gets results for query
def datamuse( word, usecase):
	base_url = "http://api.datamuse.com/words"
	query_base = 'rel_'
	query_type = ''

	usecase = usecase.lower()
	if (usecase == 'syn' or usecase == 'synonym' or usecase == 'synonyms') :
		query_type = 'syn'
	if (usecase == 'ant' or usecase == 'antonym' or usecase == 'antonyms') :
		query_type = 'ant'
	if (usecase == 'rhy' or usecase == 'rhyming' or usecase == 'rhymes' ) :
		query_type = 'rhy'
	if (usecase == 'hom' or usecase == 'homophone' or usecase == 'homophones') :
		query_type = 'hom'
	query_base += query_type

	req_param = {query_base : word}

	#Fires query to Datamuse API through the python requests lib
	word = requests.get(url = base_url,params = req_param)

	#Converted above object to dictionary of tuples
	word2json = word.json()

	tweet_string = ''
	for dict_value in word2json :
		for tuple_val in dict_value.items() :
			if(tuple_val[0] == 'word') :
				tweet_string += tuple_val[1] + ', '
	tweet_string = tweet_string[:-2]

	return tweet_string



#Function to construct the string that will be tweeted as a reply
def processTweet(tweets, username) :
	
	#Splitting tweet into words
	tweet_list = tweets.split()

	#Iterate through list to find word and usecase
	for i in range(0, len(tweet_list)-2) :
		if tweet_list[i] == '@wordnerd_bot' :
			query_word = tweet_list[i+1]
			query_usecase = tweet_list[i+2]
			break

	#Adding the username of the user that tweeted
	final_tweet = f" @{username} {query_word} {query_usecase} is "
	final_tweet += datamuse(query_word, query_usecase)

	if len(final_tweet) > 280 :
		final_tweet = final_tweet[:280 - len(final_tweet)]
		for i in range(len(final_tweet)-1,0,-1) :
			if final_tweet[i] == ',':
				final_tweet = final_tweet[:i]
				break

	return final_tweet



#Driver function.Checks for new tweets every 2 minutes
def main() :
	
	#Pre filtering tweets by keywords
	keywords = ['syn','synonym','synonyms','ant','antonym','antonyms','rhy','rhyming','rhymes','hom','homophone','homophones']
	prev_id = 1

	#Keeps checking after every 120 seconds
	while True :
		prev_id = mentioned_reply (keywords,prev_id)
		time.sleep(120)

#main func
if __name__ == '__main__' :
	main()
