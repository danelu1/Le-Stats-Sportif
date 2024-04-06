'''
Module used to parse the data from the CSV file and provide the necessary
data structures to the TaskRunner.
'''

import csv

class DataIngestor:
    '''
    Class used to parse the data from the CSV file and provide the necessary
    data structures to the TaskRunner In the __init__ method, the csv file is
    opened and I extract in a list every tuple containing the state, the value,
    the question, the category and the category value, which I use further to
    create a dictionary where each key represents a tuple containing the
    question and the state that has the question, and the value is a list
    of all the values that the state has for that question. I also do the
    same for the categories but with a dictionary containing the question,
    the state, the category and the category value as the key and the list
    of values as the value.
    '''
    def __init__(self, csv_path: str):
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_file = csv.reader(file)
            states_stats = [(x[4], x[11], x[8], x[30], x[31]) for x in csv_file if x[11] != ''][1:]
            self.data = {(question, state): [] for (state, _, question, _, _) in states_stats}

            for state, stat, question, _, _ in states_stats:
                self.data[(question, state)].append(float(stat))

            self.data_by_category = {(question, state, category, category_value): [] for (state, _, question, category, category_value) in states_stats}

            for state, stat, question, category, category_value in states_stats:
                item = (question, state, category, category_value)
                self.data_by_category[item].append(float(stat))

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

    def helper(self, question):
        '''
    	This is a helper function used to filter all those states that have a
    	certain question given as a parameter and return a dictionary where the
    	key is the state and the value is the list of values that the state has
    	for that question.
    	'''
        items_by_question = list(filter(lambda x: x[0] == question, self.data.keys()))
        return {state: self.data[(question, state)] for (_, state) in items_by_question}
