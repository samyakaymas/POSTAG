from operator import itemgetter				#this functionality is NOT needed. It may help slightly, but you can definitely ignore it completely.
import time
import math
#DO NOT CHANGE!
def read_train_file():
	'''
	HELPER function: reads the training files containing the words and corresponding tags.
	Output: A tuple containing 'words' and 'tags'
	'words': This is a nested list - a list of list of words. See it as a list of sentences, with each sentence itself being a list of its words.
	For example - [['A','boy','is','running'],['Pick','the','red','cube'],['One','ring','to','rule','them','all']]
	'tags': A nested similar to above, just the corresponding tags instead of words. 
	'''						
	f = open('train','r')
	words = []
	tags = []
	lw = []
	lt = []
	for line in f:
		s = line.rstrip('\n')
		w,t= s.split('/')[0],s.split('/')[1]
		if w=='###':
			words.append(lw)
			tags.append(lt)
			lw=[]
			lt=[]
		else:
			lw.append(w)
			lt.append(t)
	words = words[1:]
	tags = tags[1:]
	assert len(words) == len(tags)
	f.close()
	return (words,tags)
#NEEDS TO BE FILLED!
def train_func(train_list_words, train_list_tags):

	'''
	This creates dictionaries storing the transition and emission probabilities - required for running Viterbi. 
	INPUT: The nested list of words and corresponding nested list of tags from the TRAINING set. This passing of correct lists and calling the function
	has been done for you. You only need to write the code for filling in the below dictionaries. (created with bigram-HMM in mind)
	OUTPUT: The two dictionaries

	HINT: Keep in mind the boundary case of the starting POS tag. You may have to choose (and stick with) some starting POS tag to compute bigram probabilities
	for the first actual POS tag.
	'''
	data = [train_list_words,train_list_tags]
	total_tags = ['SOS','EOS']
	dict2_tag_follow_tag= {}
	dict2_tag_follow_tag['SOS'] = {}
	for seq in data[1]:
		prev = 'SOS'
		for tag in seq:
			if tag not in total_tags:
				total_tags.append(tag)
			next = tag
			if prev not in list(dict2_tag_follow_tag.keys()):
				dict2_tag_follow_tag[prev] = {}
				dict2_tag_follow_tag[prev][next] = 1
			else:
				if next not in list(dict2_tag_follow_tag[prev].keys()):
					dict2_tag_follow_tag[prev][next] = 1
				else:
					dict2_tag_follow_tag[prev][next] += 1
			prev = next
		next = 'EOS'
		if prev not in list(dict2_tag_follow_tag.keys()):
			dict2_tag_follow_tag[prev] = {}
			dict2_tag_follow_tag[prev][next] = 1
		else:
			if next not in list(dict2_tag_follow_tag[prev].keys()):
				dict2_tag_follow_tag[prev][next] = 1
			else:
				dict2_tag_follow_tag[prev][next] += 1

	for tags in total_tags:
		count = 0
		if tags not in list(dict2_tag_follow_tag.keys()):
			dict2_tag_follow_tag[tags] = {}
			for tag in total_tags:
				dict2_tag_follow_tag[tags][tag] = 0.0000000000000001
		else:
			for tag in total_tags:
				if tag not in list(dict2_tag_follow_tag[tags].keys()):
					dict2_tag_follow_tag[tags][tag] = 0.000000000000001
				else:
					count += dict2_tag_follow_tag[tags][tag]
		for tag in total_tags:
			if count != 0:
				dict2_tag_follow_tag[tags][tag] /= count
	"""   Nested dictionary to store the transition probabilities
	each tag X is a key of the outer dictionary with an inner dictionary as the corresponding value
	The inner dictionary's key is the tag Y following X
	and the corresponding value is the number of times Y follows X - convert this count to probabilities finally before returning	"""
	count = {}
	for tags in total_tags:
		count[tags] = 0
		dict2_word_tag = {}
	for i in range(len(data[0])):
		for j in range(len(data[0][i])):
			count[data[1][i][j]] += 1
			if data[0][i][j] not in list(dict2_word_tag.keys()):
				dict2_word_tag[data[0][i][j]] = {}
			if data[1][i][j] not in list(dict2_word_tag[data[0][i][j]].keys()):
				dict2_word_tag[data[0][i][j]][data[1][i][j]] = 1
			else:
				dict2_word_tag[data[0][i][j]][data[1][i][j]] += 1
	
	for words in list(dict2_word_tag.keys()):
		for tags in list(dict2_word_tag[words].keys()):
			dict2_word_tag[words][tags] /= count[tags]
	'''
	
		dict2_word_tag[tags] = {}
	for i in range(len(data[0])):
		for j in range(len(data[0][i])):
			count[data[1][i][j]] += 1
			if data[0][i][j].lower() not in list(dict2_word_tag[data[1][i][j]].keys()):
				dict2_word_tag[data[1][i][j]][data[0][i][j].lower()] = 1
			else:
				dict2_word_tag[data[1][i][j]][data[0][i][j].lower()] += 1
	for tags in total_tags:
		for word in list(dict2_word_tag[tags].keys()):
			dict2_word_tag[tags][word] /= count[tags]
	'''
	"""Nested dictionary to store the emission probabilities.
	Each word W is a key of the outer dictionary with an inner dictionary as the corresponding value
	The inner dictionary's key is the tag X of the word W
	and the corresponding value is the number of times X is a tag of W - convert this count to probabilities finally before returning
	"""


	#      *** WRITE YOUR CODE HERE ***    

	# END OF YOUR CODE	

	return (dict2_tag_follow_tag, dict2_word_tag, total_tags)
#NEEDS TO BE FILLED!
def assign_POS_tags(test_words, dict2_tag_follow_tag, dict2_word_tag, total_tags):

	'''
	This is where you write the actual code for Viterbi algorithm. 
	INPUT: test_words - this is a nested list of words for the TEST set
	       dict2_tag_follow_tag - the transition probabilities (bigram), filled in by YOUR code in the train_func
	       dict2_word_tag - the emission probabilities (bigram), filled in by YOUR code in the train_func
	OUTPUT: a nested list of predicted tags corresponding to the input list test_words. This is the 'output_test_tags' list created below, and returned after your code
	ends.

	HINT: Keep in mind the boundary case of the starting POS tag. You will have to use the tag you created in the previous function here, to get the
	transition probabilities for the first tag of sentence...
	HINT: You need not apply sophisticated smoothing techniques for this particular assignment.
	If you cannot find a word in the test set with probabilities in the training set, simply tag it as 'N'. 
	So if you are unable to generate a tag for some word due to unavailibity of probabilities from the training set,
	just predict 'N' for that word.

	'''



	output_test_tags = []    #list of list of predicted tags, corresponding to the list of list of words in Test set (test_words input to this function)
	

	#      *** WRITE YOUR CODE HERE ***
	for line in test_words:
		dp = [ dict() for i in range(len(line)+1) ]
		best_tag = [ dict() for j in range(len(line)+1)]
		dp[0]['SOS'] = 0.0
		for i in range(len(line)):
			if line[i] not in list(dict2_word_tag.keys()):
				dict2_word_tag[line[i]] = {}
				#Taking unknown words to be Noun VErb Adjective Cardinal with equal probabilities(It increases the accuracy against only taking it as Noun)
				for temp in 'N' 'V' 'J' 'C':
					dict2_word_tag[line[i]][temp] = 0.25
			for prev in list(dp[i].keys()):
				for next_tag in total_tags:
					score = -1.0
					if next_tag in list(dict2_word_tag[line[i]].keys()) and dict2_tag_follow_tag[prev][next_tag]!=0 :
						score = 1.5*dp[i][prev] - math.log(dict2_tag_follow_tag[prev][next_tag]) - math.log(dict2_word_tag[line[i]][next_tag])
						if next_tag not in list(dp[i+1].keys()) or dp[i+1][next_tag] > score:
							dp[i+1][next_tag] = score
							best_tag[i+1][next_tag] = prev

		for tags in list(dp[len(line) - 1].keys()):
			if dict2_tag_follow_tag[tags]['EOS'] != 0:
				score = dp[len(line) - 1][tags] - math.log(dict2_tag_follow_tag[tags]['EOS'])
				if 'EOS' not in list(dp[len(line)].keys()) or dp[len(line)]['EOS'] > score:
					dp[len(line)]['EOS'] = float(score)
					best_tag[len(line)]['EOS'] = tags

		final_tags = [ '' for i in range(len(best_tag))]
		last = 'EOS'
		for i in range(len(best_tag)-1,0,-1):
			final_tags[i] = best_tag[i][last]
			last = best_tag[i][last]
		
		final_tags.append('.')

		output_test_tags.append(final_tags[2:])

	# END OF YOUR CODE

	return output_test_tags









# DO NOT CHANGE!
def public_test(predicted_tags):
	'''
	HELPER function: Takes in the nested list of predicted tags on test set (prodcuced by the assign_POS_tags function above)
	and computes accuracy on the public test set. Note that this accuracy is just for you to gauge the correctness of your code.
	Actual performance will be judged on the full test set by the TAs, using the output file generated when your code runs successfully.
	'''

	f = open('test_public_labeled','r')
	words = []
	tags = []
	lw = []
	lt = []
	for line in f:
		s = line.rstrip('\n')
		w,t= s.split('/')[0],s.split('/')[1]
		if w=='###':
			words.append(lw)
			tags.append(lt)
			lw=[]
			lt=[]
		else:
			lw.append(w)
			lt.append(t)
	words = words[1:]
	tags = tags[1:]
	assert len(words) == len(tags)
	f.close()
	public_predictions = predicted_tags[:len(tags)]
	assert len(public_predictions)==len(tags)

	correct = 0
	total = 0
	flattened_actual_tags = []
	flattened_pred_tags = []
	for i in range(len(tags)):
		x = tags[i]
		y = public_predictions[i]
		if len(x)!=len(y):
			print(i)
			print(x)
			print(y)
			break
		flattened_actual_tags+=x
		flattened_pred_tags+=y
	assert len(flattened_actual_tags)==len(flattened_pred_tags)
	correct = 0.0
	for i in range(len(flattened_pred_tags)):
		if flattened_pred_tags[i]==flattened_actual_tags[i]:
			correct+=1.0
		#else:
			#print(flattened_pred_tags[i],flattened_actual_tags[i])
	print('Accuracy on the Public set = '+str(correct/len(flattened_pred_tags)))



# DO NOT CHANGE!
def evaluate():
	words_list_train = read_train_file()[0]
	tags_list_train = read_train_file()[1]

	( dict2_tag_tag ,dict2_word_tag, total_tags ) = train_func(words_list_train,tags_list_train)

	f = open('test_full_unlabeled','r')

	words = []
	l=[]
	for line in f:
		w = line.rstrip('\n')
		if w=='###':
			words.append(l)
			l=[]
		else:
			l.append(w)
	f.close()
	words = words[1:]
	test_tags = assign_POS_tags(words, dict2_tag_tag, dict2_word_tag, total_tags)
	assert len(words)==len(test_tags)
	public_test(test_tags)

	#create output file with all tag predictions on the full test set

	f = open('output','w')
	f.write('###/###\n')
	for i in range(len(words)):
		sent = words[i]
		pred_tags = test_tags[i]
		for j in range(len(sent)):
			word = sent[j]
			pred_tag = pred_tags[j]
			f.write(word+'/'+pred_tag)
			f.write('\n')
		f.write('###/###\n')
	f.close()

	print('OUTPUT file has been created')

if __name__ == "__main__":
	start = time.time()
	evaluate()
	print('Time Taken :',time.time() - start ,'Seconds')
