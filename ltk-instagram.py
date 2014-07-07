#!/usr/bin/python

from config import *

import bottle_session
import bottle
from bottle import route, redirect, post, run, request
from instagram.instagram import client, subscriptions

bottle.debug(True)

app = bottle.app()
plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
app.install(plugin)

CONFIG = {
	'client_id': client_id,
	'client_secret': client_secret,
	'redirect_uri': redirect_uri
}

unauthenticated_api = client.InstagramAPI(**CONFIG)

def process_tag_update(update):
	print update

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)

@route('/')
def home():
	try:
		url = unauthenticated_api.get_authorize_url(scope=["likes","comments"])
		return '<a href="%s">Connect with Instagram</a>' % url
	except Exception, e:
		print e

def count_items(items):
	count=0
	for i in items:
		count+=1
	return str(count)

def get_follows(access_token):
	user_follows = []
	if not access_token:
		return 'Missing Access Token'
	try:
		api = client.InstagramAPI(access_token=access_token)
		follows, next = api.user_follows()
		for follow in follows:
			user_follows.append(follow.username)
		while next:
			follows, next = api.user_follows(with_next_url=next)
			for follow in follows:
				user_follows.append(follow.username)
	except Exception, e:
		print e
	return user_follows

def get_followed_by(access_token):
	user_followed_by = []
	if not access_token:
		return 'Missing Access Token'
	try:
		api = client.InstagramAPI(access_token=access_token)
		followed_by, next = api.user_followed_by()
		for follower in followed_by:
			user_followed_by.append(follower.username)
		while next:
			followed_by, next = api.user_followed_by(with_next_url=next)
			for follower in followed_by:
				user_followed_by.append(follower.username)
	except Exception, e:
		print e
	return user_followed_by

def get_liked_media(access_token):
	liked_media = {}
	if not access_token:
		return 'Missing Access Token'
	try:
		api = client.InstagramAPI(access_token=access_token)
		likes, next = api.user_liked_media()
		for like in likes:
			print like
		while next:
			likes, next = api.user_liked_media(with_next_url=next)
			for like in likes:
				print like
	except Exception, e:
		print e
	return liked_media

def get_not_following(follows, followed_by):
	not_following = []
	for u in followed_by:
		if u not in follows:
			not_following.append(u)
	return not_following

def get_not_followed_by(follows, followed_by):
	not_followed_by = []
	for u in follows:
		if u not in followed_by:
			not_followed_by.append(u)
	return not_followed_by

def get_nav(access_token, api):

	print "Getting follows..."
	follows = get_follows(access_token)

	print "Getting followed_by..."
	followed_by = get_followed_by(access_token)

	follows_count = count_items(follows)
	followed_by_count = count_items(followed_by)

	print "Getting not following..."
	not_following = get_not_following(follows, followed_by)
	not_following_count = count_items(not_following)

	print "Getting not followed by..."
	not_followed_by = get_not_followed_by(follows, followed_by)
	not_followed_by_count = count_items(not_followed_by)

	print "Getting liked media..."
	liked_media = get_liked_media(access_token)
	liked_media_count = count_items(liked_media)

	nav_menu = ("<h1>LTK Instagram</h1>"
				"<p>Hello world!</p>")

	nav_menu += 'Follows: ' + follows_count + '<br>'
	#print follows

	nav_menu += 'Followed By: ' + followed_by_count + '<br>'
	#print followed_by

	nav_menu += 'Not Following: ' + not_following_count + '<br>'
	#print not_following

	nav_menu += 'Not Followed By: ' + not_followed_by_count + '<br>'
	#print not_followed_by

	nav_menu += 'Liked Media: ' + liked_media_count + '<br>'
	print liked_media
	
	return nav_menu

@route('/oauth_callback')
def on_callback(session):
	code = request.GET.get("code")
	if not code:
		return 'Missing code'
	try:
		access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
		print "access token= " + access_token
		if not access_token:
			return 'Could not get access token'
		api = client.InstagramAPI(access_token=access_token)
		session['access_token']=access_token
	except Exception, e:
		access_token = None
		print e
	return get_nav(access_token, api)

run(host='localhost', port=port_number, reloader=True)
