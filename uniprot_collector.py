#!/usr/bin/python env
# -*- coding: utf-8 -*-

"""
Description:
"""

__author__ = "joshliu"


import sys
import time
import os
import datetime
from urllib import request

from selenium import webdriver
from selenium.webdriver.common import action_chains, keys


DIRNAME = datetime.datetime.now().strftime('%b-%d-%Y-%H-%M-%S')


def save(filename, content, dirname = ''):
	if len(content) == 0:
		return

	path = os.curdir + os.sep
	if len(dirname) > 0:
		path += dirname + os.sep
	else:
		path += DIRNAME + os.sep
	path += filename

	if not os.path.exists(os.path.dirname(path)):
		os.mkdir(os.path.dirname(path))

	with open(path, mode='w') as fd:
		fd.write(content)
	return


def initProteinList(filepath):
	with open(filepath) as fd:
		fd.readline()
		for line in fd.readlines():
			line.replace('\n', '')
			if len(line) == 0:
				continue
			print('initProteinList ' + line)
			proteinList.append(line.split('\t')[0])


def initOutputFileIfNeeded(filepath):
	if not os.path.exists(filepath):
		with open(filepath, mode='w') as fd:
			firstLine = ['protein', 'sequence', 'PRDlen', 'PROTlen', 'IUPREDScore', 'IUPREDNum']
			fd.write('\t'.join(firstLine) + '\n')


inputFileName = '/Users/joshualiu/Desktop/prot2.txt'
outputFileName = os.path.basename(inputFileName) + '.csv'
proteinList = []
seqList = []
PRDlenList = []
PROTlenList = []
IUPREDScoreList = []
IUPREDNumList = []
browser = webdriver.Chrome()
initOutputFileIfNeeded(outputFileName)
initProteinList(outputFileName)
with open(inputFileName) as fd:
	for protein in fd.readlines():
		protein = protein.replace('\n', '')
		if protein in proteinList:
			continue

		done = False
		while not done:
			try:
				print(protein)
				proteinList.append(protein)
				browser.get('https://www.uniprot.org/uniprot/' + protein + '.fasta')
				element = browser.find_element_by_tag_name('pre')

				assert element, 'sequence not found ' + protein

				seq = ''
				for tmpSeq in element.text.split('\n')[1:]:
					seq += tmpSeq
				print('sequence ' + seq)
				seqList.append(seq)

				browser.get('http://plaac.wi.mit.edu/')
				element = browser.find_element_by_id('sequence')
				element.send_keys(seq)

				actions = action_chains.ActionChains(browser)
				element = browser.find_element_by_id('run_analysis')
				actions.click(element)
				actions.perform()

				element = browser.find_element_by_class_name('btn-success')
				href = element.get_attribute('href')

				assert href, 'PRD not found ' + protein

				print(href)
				resp = request.urlopen(href, timeout=60)
				tsvContent = resp.read().decode()
				tsvSeq = ''
				for line in tsvContent.split('\n'):
					if line.startswith('sequence'):
						tsvSeq = line
				PRDlen = tsvSeq.split('\t')[18]
				PROTlen = tsvSeq.split('\t')[19]
				print('PRDlen ' + PRDlen + 'PROTlen ' + PROTlen)
				PRDlenList.append(PRDlen)
				PROTlenList.append(PROTlen)

				browser.get('https://iupred2a.elte.hu/')
				element = browser.find_element_by_id('accession')
				element.send_keys(protein)
				element.send_keys(keys.Keys.ENTER)
				element = browser.find_element_by_tag_name('form')
				href = element.get_attribute('action')
				browser.get(href)
				element = browser.find_element_by_tag_name('pre')

				assert element, 'IUPRED not found ' + protein

				IUPredContent = element.text
				IUPREDScore = 0
				IUPREDScoreNum = len(IUPredContent.split('\n'))
				for line in IUPredContent.split('\n'):
					if line.find('#') != -1:
						continue
					if float(line.split(' ')[2]) > 0.5:
						IUPREDScore += 1
				print('IUPREDScore' + str(IUPREDScore) + 'IUPREDScoreNum' + str(IUPREDScoreNum))
				IUPREDScoreList.append(IUPREDScore)
				IUPREDNumList.append(IUPREDScoreNum)

				with open(outputFileName, mode='a') as fd:
					fd.write(protein + '\t' + seq
					         + '\t' + str(PRDlen) + '\t' + str(PROTlen)
					         + '\t' + str(IUPREDScore) + '\t' + str(IUPREDScoreNum) + '\n')
					done = True

			except:
				browser.close()
				time.sleep(30)
				browser = webdriver.Chrome()
				continue

# resultfilename = os.path.basename(inputFileName)
# with open(resultfilename, mode='w') as fd:
# 	firstLine = ['protein', 'sequence', 'PRDlen', 'PROTlen', 'IUPREDScore', 'IUPREDNum']
# 	fd.write('\t'.join(firstLine))
# 	for i in range(0, len(proteinList)):
# 		fd.write(proteinList[i] + '\t' + seqList[i]
# 		         + '\t' + PRDlenList[i] + '\t' + PROTlenList[i]
# 		         + '\t' + IUPREDScoreList[i] + '\t' + IUPREDNumList[i])
