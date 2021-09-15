#!/usr/bin/env python3
import os
import logging
from IUBBaseTools import ApiHandler, IUBConfiguration
from random import randint
from time import sleep


#Check if the given path is an absolute path
def createAbsolutePath(path):
	if not os.path.isabs(path):
		currentDir = os.path.dirname(os.path.realpath(__file__))
		path = os.path.join(currentDir, path)

	return path


def extractRequestedMaterial(received, requested):
	toReturn = []
	for material in requested:
		if material not in received:
			logging.warning("Attention - material: "+material+" not used by IUB")
		else:
			toReturn.append(material)
	return toReturn


def main():
	configFile = "config.yml"
	logFile = "order_account.log"
	#Set logging file
	logging.basicConfig(filename=createAbsolutePath(logFile), level=logging.ERROR, format='%(asctime)s %(levelname)-8s %(message)s')
	#Load config
	config_class = IUBConfiguration(createAbsolutePath(configFile), logging)
	logging.getLogger().setLevel(config_class.get_config('GlobalSettings', 'logLevel'))
	logging.info('Loaded settings started')

	#Creates handler to send request to the backend site
	handler = ApiHandler(
		config_class.get_config('GlobalSettings', 'username'),
		config_class.get_config('GlobalSettings', 'urlHandler'),
		config_class.get_config('GlobalSettings', 'tokenPath'),
		logging)

	#Get all materials
	all_material = handler.getAllReleases(config_class.get_config('GlobalSettings', 'material_list'))

	#Create an array of materials
	#Iterate over genres
	for code in all_material:
		#Iterate over accounts
		try:
			response = handler.orderThisRelease(code)
			#Check response
			if response == "Premium directory not found":
				print("Skip release "+str(code)+": no sufficient information")
				logging.warning("Skip release "+str(code)+": no sufficient information")
			elif response:
				print("Release " + str(code) + " ordered")
				logging.info("Release " + str(code) + " ordered")
			else:
				print("Unexpected error release "+str(code)+": See log")
				logging.error("Unexpected error release "+str(code)+": "+str(response))

			#Check if everything is inserted
			sleep(randint(
				config_class.get_config('GlobalSettings', 'min_sleep_time'),
				config_class.get_config('GlobalSettings', 'max_sleep_time')))
		except Exception as exc:
			logging.error("STOP: Unexpected exception: "+str(exc))
			return
	logging.info("END: Ordered "+str(len(all_material))+" objects")


main()
