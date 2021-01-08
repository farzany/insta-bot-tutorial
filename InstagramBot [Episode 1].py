from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
import random
import numpy

class InstagramBot:

	def __init__(self,username,password):
		self.loggedin = False
		self.username = username
		self.password = password
		self.base_url = "https://www.instagram.com"
		self.followersCount = 0
		self.followingCount = 0
		self.followedList = []
		self.doNotFollowList = []
		self.whitelist = []
		self.CreateFiles()
		self.Choose()

	################# Chooser #################

	def Choose(self):
		# The UI
		if not self.loggedin:
			self.Login()
			self.GetInfo()
		print(".................")
		choice = input("[1] Follow Followers\n[2] Unfollow Followed\nChoice:\t")
		if choice == "1":
			self.FollowFollowers()
		elif choice == "2":
			self.UnfollowFollowed()
		elif choice == "q":
			return
		
		self.Choose()

	################# Helper Methods #################

	def ConvertToNumber(self, text):
		# Converts instagram's shorthand to a number
		if "k" in text:
			return int((float(text.replace("k","")))*1000)
		elif "m" in text:
			return int((float(text.replace("m","")))*1000000)
		else:
			return int(text)
	
	def Wait(self,min,max):
		# Pauses for a random amount of time
		time.sleep(random.choice(numpy.arange(min,max,0.1)))

	def GoToUser(self, user):
		# Goes to a user's page
		self.driver.get("{}/{}/".format(self.base_url, user))
		self.Wait(1,2)

	def UnfollowUser(self, user):
		# Unfollows a user through their page
		self.GoToUser(user)
		div = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/div[1]")
		button = div.find_elements_by_xpath(".//button")
		if (button and button[0].text != "Follow"):
			if (len(button) > 2):
				button[1].click()
			else:
				button[0].click()
			self.Wait(1,1.5)
			self.driver.find_element_by_xpath("/html/body/div[5]/div/div/div/div[3]/button[1]").click()

	def CreateFiles(self):
		# Creates files for user if they don't exist
		temp = open("[Followed][{}]".format(self.username), "a+")
		temp.close
		temp = open("[DoNotFollow][{}]".format(self.username), "a+")
		temp.close

	def ReadFiles(self):
		# Obtains previously followed usernames from file
		self.Wait(1,1.5)
		self.followedList = []
		self.doNotFollowList = []
		with open("[Followed][{}]".format(self.username), "r+") as flist:
			lines = flist.readlines()
			for line in lines:
				self.followedList.append(line.strip())
		with open("[DoNotFollow][{}]".format(self.username), "r+") as flist:
			lines = flist.readlines()
			for line in lines:
				self.doNotFollowList.append(line.strip())

	def AddFollowedList(self, name):
		# Appends followed username to files
		with open("[Followed][{}]".format(self.username), "a+") as flist:
			temp = name.strip() + "\n"
			flist.write(temp)
		with open("[DoNotFollow][{}]".format(self.username), "a+") as flist:
			temp = name.strip() + "\n"
			flist.write(temp)
	
	def RemFollowedList(self, name):
		# Removes followed username from file
		with open("[Followed][{}]".format(self.username), "r") as flist:
			lines = flist.readlines()
		with open("[Followed][{}]".format(self.username), "w") as flist:
			for line in lines:
				if line.strip() != name:
					flist.write(line)


	################# Logging In #################

	def Login(self):
		self.driver = webdriver.Chrome("chromedriver.exe")
		print("Logging In: {}".format(self.username))
		self.driver.get("{}/accounts/login".format(self.base_url))
		self.Wait(2,3)
		self.driver.find_element_by_name("username").send_keys(self.username)
		self.Wait(1,2)
		self.driver.find_element_by_name("password").send_keys(self.password)
		self.Wait(1,2)
		self.driver.find_elements_by_xpath("//div[contains(text(), 'Log In')]")[0].click()
		print("Logged In: {}".format(self.username))
		self.loggedin = True
		self.Wait(5,6)

	def GetInfo(self):
		# Gets followers & following amounts
		self.GoToUser(self.username)
		# Get number of followers
		temp = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[2]/a/span").text
		self.followersCount = self.ConvertToNumber(temp)
		# Get number of following
		temp = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[3]/a/span").text
		self.followingCount = self.ConvertToNumber(temp)
		# print(self.followersCount, self.followingCount)


	################# Following Followers #################

	def FollowFollowers(self):
		# Follows the followers of a user
		# Gets username and number of followers to follow
		self.ReadFiles() # In case of any changes to files
		user = input("Account username:\t")
		self.GoToUser(user)
		temp = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[2]/a/span").text
		numoffollowers = self.ConvertToNumber(temp)
		amount = int(input("How many to follow? (Less than {})\t".format(temp)))
		while amount > numoffollowers:
			amount = int(input("How many to follow? (Less than {})\t".format(temp)))

		# Clicks followers tab and goes through the list one by one
		self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[2]/a").click()
		i, k = 1, 1
		while (k <= amount):
			self.Wait(1,1.5)
			currentUser = self.driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/ul/div/li[{}]".format(i))
			button = currentUser.find_elements_by_xpath(".//button")
			name = currentUser.find_element_by_css_selector(".notranslate").text
			# If a strictly "Follow" button exists, it clicks it
			if (button) and (button[0].text == "Follow") and (name not in self.doNotFollowList):
				self.Wait(10,15)
				button[0].click()
				self.AddFollowedList(name) # Writes username to file
				print("[{}] {} followed {}".format(k, self.username, name))
				k += 1
			self.Wait(1,1.5)
			# Scrolls down for the user to be at the top of the tab
			self.driver.execute_script("arguments[0].scrollIntoView()", currentUser)
			i += 1

	################# Unfollowing Followed #################

	def UnfollowFollowed(self):
		self.ReadFiles() # In case of any changes to files
		numoffollowed = len(self.followedList)
		amount = int(input("How many to unfollow? (followed {})\t".format(numoffollowed)))
		while amount > numoffollowed:
			amount = int(input("How many to unfollow? (followed {})\t".format(numoffollowed)))

		for i in range(amount):
			user = self.followedList[i]
			self.Wait(10,15)
			self.UnfollowUser(user)
			self.RemFollowedList(user)
			print("[{}] {} unfollowed {}".format(i+1, self.username, user))
		
		self.ReadFiles() # Update lists after removing from them

TestRuns = InstagramBot("your username", "your password")

	
