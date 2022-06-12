from matplotlib.style import available
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
		self.commentlist = []
		self.CreateFiles()
		self.Choose()

	################# Chooser #################

	def Choose(self):
		# The UI
		if not self.loggedin:
			self.Login()
			self.GetInfo()
		print(".................")
		choice = input("[1] Follow Followers\n[2] Unfollow Followed\n[3] Unfollow All\n[4] Tag Options\nChoice:\t")
		if choice == "1":
			self.FollowFollowers()
			self.Choose()
		elif choice == "2":
			self.UnfollowFollowed()
			self.Choose()
		elif choice == "3":
			self.UnfollowAll()
			self.Choose()
		elif choice == "4":
			self.TagOptions()
			self.Choose()
		elif choice == "q":
			self.driver.close()
			return

	################# Helper Methods #################

	def ConvertToNumber(self, text):
		# Converts instagram's shorthand to a number
		if "K" in text:
			return int((float(text.replace("K","")))*1000)
		elif "M" in text:
			return int((float(text.replace("M","")))*1000000)
		else:
			return int(text)
	
	def Wait(self,min,max):
		# Pauses for a random amount of time
		time.sleep(random.choice(numpy.arange(min,max,0.1)))

	def GoToUser(self, user):
		# Goes to a user's page
		self.driver.get("{}/{}/".format(self.base_url, user))
		self.Wait(3,4)

	def UnfollowUser(self, user):
		# Unfollows a user through their page
		self.GoToUser(user)

		notFollowed = self.driver.find_elements_by_xpath("//*[text()='Follow']")
		unavailable = self.driver.find_elements_by_xpath("//*[contains(text(), 'broken')]")

		if not unavailable and not notFollowed:
			button = self.driver.find_element_by_xpath("//button[@class='_abn9 _abnd _abni _abnn']")
			button.click()
			self.Wait(1,1.5)
			self.driver.find_element_by_xpath("//*[text()='Unfollow']").click()

	def CreateFiles(self):
		# Creates files for user if they don't exist
		temp = open("[Followed][{}]".format(self.username), "a+")
		temp.close
		temp = open("[DoNotFollow][{}]".format(self.username), "a+")
		temp.close
		temp = open("[Whitelist][{}]".format(self.username), "a+")
		temp.close
		temp = open("[Comments][{}]".format(self.username), "a+")
		temp.close

	def ReadFiles(self):
		# Obtains previously followed usernames from file
		self.Wait(1,1.5)
		self.followedList = []
		self.doNotFollowList = []
		self.whitelist = []
		with open("[Followed][{}]".format(self.username), "r+") as flist:
			lines = flist.readlines()
			for line in lines:
				self.followedList.append(line.strip())
		with open("[DoNotFollow][{}]".format(self.username), "r+") as flist:
			lines = flist.readlines()
			for line in lines:
				self.doNotFollowList.append(line.strip())
		with open("[Whitelist][{}]".format(self.username), "r+") as flist:
			lines = flist.readlines()
			for line in lines:
				self.whitelist.append(line.strip())
		with open("[Comments][{}]".format(self.username), "r+") as flist:
			lines = flist.readlines()
			for line in lines:
				self.commentlist.append(line.strip())

	def AddFollowedList(self, name):
		# Appends followed username to files
		with open("[Followed][{}]".format(self.username), "a+") as flist:
			temp = name.strip() + "\n"
			flist.write(temp)
		self.ReadFiles()

	def AddDoNotFollowList(self, name):
		# Adds a user to DoNotFollow file
		with open("[DoNotFollow][{}]".format(self.username), "a+") as flist:
			temp = name.strip() + "\n"
			flist.write(temp)
		self.ReadFiles()
	
	def RemFollowedList(self, name):
		# Removes followed username from file
		with open("[Followed][{}]".format(self.username), "r") as flist:
			lines = flist.readlines()
		with open("[Followed][{}]".format(self.username), "w") as flist:
			for line in lines:
				if line.strip() != name:
					flist.write(line)
		self.ReadFiles()


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
		temp = self.driver.find_elements_by_xpath('//span[@class="_ac2a"]')[0].text
		self.followersCount = self.ConvertToNumber(temp)
		# Get number of following
		temp = self.driver.find_elements_by_xpath('//span[@class="_ac2a"]')[1].text
		self.followingCount = self.ConvertToNumber(temp)
		# print(self.followersCount, self.followingCount)
		self.ReadFiles()


	################# Following Followers #################

	def FollowFollowers(self):
		# Follows the followers of a user
		# Gets username and number of followers to follow
		self.ReadFiles() # In case of any changes to files
		user = input("Account username:\t")
		self.GoToUser(user)
		temp = self.driver.find_elements_by_xpath("//span[@class='_ac2a']")[1].text
		
		numoffollowers = self.ConvertToNumber(temp)
		amount = int(input("How many to follow? (Less than {})\t".format(temp)))
		while amount > numoffollowers:
			amount = int(input("How many to follow? (Less than {})\t".format(temp)))

		# Clicks followers tab and goes through the list one by one
		self.GoToUser(user + "/followers")
		i, k = 1, 1
		while (k <= amount):
			self.Wait(1,1.5)
			currentUser = self.driver.find_element_by_xpath('//div[@class="_aae-"]/li[{}]'.format(i))
			button = currentUser.find_elements_by_xpath(".//button")
			name = currentUser.find_element_by_css_selector(".notranslate").text
			# If a strictly "Follow" button exists, it clicks it
			if (button) and (button[0].text == "Follow") and (name not in self.doNotFollowList):
				self.Wait(30,35)
				button[0].click()
				self.AddFollowedList(name) # Writes username to file
				self.AddDoNotFollowList(name)
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
			user = self.followedList[0]
			self.Wait(10,15)
			self.UnfollowUser(user)
			self.RemFollowedList(user)
			print("[{}] {} unfollowed {}".format(i+1, self.username, user))

	################# Unfollowing All #################

	def UnfollowAll(self):
		# Unfollows a certain number of following (at random)
		# Adds names to DoNotFollow if not already there
		# Removes names from Followed if there
		self.GetInfo()
		amount = int(input("How many to unfollow? (following {})\t".format(self.followingCount)))
		while amount > self.followingCount:
			amount = int(input("How many to unfollow? (following {})\t".format(self.followingCount)))

		self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[3]/a").click()
		i, k = 1, 1
		while (k <= amount):
			self.Wait(1,1.5)
			currentUser = self.driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/ul/div/li[{}]".format(i))
			button = currentUser.find_elements_by_xpath(".//button")
			name = currentUser.find_element_by_css_selector(".notranslate").text
			# If a strictly "Following" button exists, click it
			if (button) and (button[0].text == "Following") and (name not in self.whitelist):
				self.Wait(30,35)
				button[0].click()
				if name in self.followedList:
					self.RemFollowedList(name) # Removes username from file
				if name not in self.doNotFollowList:
					self.AddDoNotFollowList(name) # Adds username to file
				self.Wait(1,2)
				# Click unfollow in prompt
				self.driver.find_element_by_xpath("/html/body/div[6]/div/div/div/div[3]/button[1]").click()
				print("[{}] {} unfollowed {}".format(k, self.username, name))
				k += 1
			self.Wait(1,1.5)
			# Scroll down for user to be at the top of the tab
			self.driver.execute_script("arguments[0].scrollIntoView();", currentUser)
			i += 1

	################# Tag Options #################
	
	def TagOptions(self):
		# Goes to a specified tag, and likes/comments/follows user
		tag = input("Tag:\t")
		amount = int(input("How many posts to go through:\t"))
		liketag, commenttag, followtag = False, False, False
		if "y" in input("Like the post? (y/n):\t").lower():
			liketag = True
		if "y" in input("Comment on the post? (y/n):\t").lower():
			commenttag = True
		if "y" in input("Follow the poster? (y/n):\t").lower():
			followtag = True
		# Go to tag
		self.driver.get("{}/explore/tags/{}".format(self.base_url, tag))
		self.Wait(1,2)
		# Click on the first post
		self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]').click()

		for i in range(amount):
			self.Wait(10,12)
			name = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a').text
			# Liking the post
			if liketag:
				self.Wait(1,2)
				likebutton = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button')
				liketext = likebutton.find_element_by_xpath(".//*[name()='svg']").get_attribute('aria-label')
				if liketext == "Like":
					likebutton.click()
					print("[{}] *liked* post by {}".format(i+1, name))
			# Commenting on the post
			if commenttag:
				self.Wait(1,2)
				temp = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form')
				temp.find_element_by_xpath(".//*[name()='textarea']").click()
				temp.find_element_by_xpath(".//*[name()='textarea']").send_keys(random.choice(self.commentlist))
				self.Wait(1,2)
				self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/button[2]').click()
				print("[{}] *commented* on post by {}".format(i+1, name))
			# Following the poster
			if followtag:
				self.Wait(1,2)
				temp = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[2]/button')
				if (temp.text == "Follow") and (name not in self.doNotFollowList):
					temp.click()
					self.AddFollowedList(name)
					self.AddDoNotFollowList(name)
					print("[{}] *followed* {}".format(i+1, name))
			# Click to next post
			if i == 0:
				self.driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div/a').click()
			else:
				self.driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div/a[2]').click()
			

TestRuns = InstagramBot("username", "password")