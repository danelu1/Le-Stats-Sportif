import os
import json
import csv

class DataIngestor:
    def __init__(self, csv_path: str):
        # TODO: Read csv from csv_path
        with open(csv_path, 'r') as file:
            csvFile = csv.reader(file)
            states_stats = [(x[4], x[11], x[8], x[30], x[31]) for x in csvFile if x[11] != ''][1:]
            self.data = {(question, state): [] for (state, _, question, _, _) in states_stats}
            
            for state, stat, question, _, _ in states_stats:
                self.data[(question, state)].append(float(stat))
                    
            self.data_by_category = {(question, state, category, category_value): [] for (state, _, question, category, category_value) in states_stats}
            
            for state, stat, question, category, category_value in states_stats:
                self.data_by_category[(question, state, category, category_value)].append(float(stat))

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
                items_by_question = list(filter(lambda x: x[0] == question, self.data.keys()))
                return {state: self.data[(question, state)] for (_, state) in items_by_question}