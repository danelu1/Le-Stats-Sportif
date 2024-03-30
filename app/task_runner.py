from queue import Queue
from threading import Thread, Event
import time
import os
from flask import jsonify
import json

class ThreadPool:
    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        if 'TP_NUM_OF_THREADS' in os.environ:
            self.num_threads = int(os.environ['TP_NUM_OF_THREADS'])
        else:
            self.num_threads = os.cpu_count()
            
        self.jobs_queue = Queue()
        
        if not os.path.exists('results'):
            os.makedirs('results')
        
    def start(self):
        for _ in range(self.num_threads):
            TaskRunner(self.jobs_queue).start()

class TaskRunner(Thread):
    def __init__(self, queue):
        # TODO: init necessary data structures
        super().__init__()
        self.question = None
        self.state = None
        self.job_id = None
        self.command = None
        self.jobs_queue = queue
        
    def states_mean_solve(self, question, data):
        characteristics = data.items()
        stats = {state: sum(numbers) / len(numbers) for ((q, state), numbers) in characteristics if q == question and len(numbers) != 0}
        sorted_stats = sorted(stats.items(), key=lambda x: x[1])
        return dict(sorted_stats)
    
    def state_mean_solve(self, question, state, data):
        return {state: sum(data[(question, state)]) / len(data[(question, state)])}
    
    def best5_solve(self, question, data, min_questions, max_questions):
        if question in min_questions:
            return dict(list(self.states_mean_solve(question, data).items())[:5])
        elif question in max_questions:
            return dict(list(self.states_mean_solve(question, data).items())[-5:])
        
    def worst5_solve(self, question, data, min_questions, max_questions):
        if question in min_questions:
            return dict(list(self.states_mean_solve(question, data).items())[-5:])
        elif question in max_questions:
            return dict(list(self.states_mean_solve(question, data).items())[:5])
    
    def global_mean_solve(self, question, data):
        mean = sum([sum(x) for x in data.values()]) / sum([len(x) for x in data.values()])
        return {"global_mean": mean}
    
    def diff_from_mean_solve(self, question, data, question_data):
        global_mean = self.global_mean_solve(question, question_data)["global_mean"]
        return {state: global_mean - self.state_mean_solve(question, state, data)[state] for (q, state) in data.keys() if q == question}
    
    def state_diff_from_mean_solve(self, question, data, question_data, state):
        return {state: self.global_mean_solve(question, question_data)["global_mean"] - self.state_mean_solve(question, state, data)[state]}
    
    def mean_by_category_solve(self, question, category_data):
        data_by_category = {x: numbers for (x, numbers) in category_data.items() if x[0] == question}
        result = {str((x[1], x[2], x[3])): sum(data_by_category[x]) / len(data_by_category[x]) for x in data_by_category.keys()}
        return dict(sorted(result.items(), key=lambda x: x[0]))
    
    def state_mean_by_category_solve(self, question, category_data, state):
        data_by_category = {x: numbers for (x, numbers) in category_data.items() if x[0] == question and x[1] == state}
        result = {str((x[2], x[3])): sum(data_by_category[x]) / len(data_by_category[x]) for x in data_by_category.keys()}
        return {state: dict(sorted(result.items(), key=lambda x: x[0]))}

    def run(self):
        while True:
            # TODO
            # Get pending job
            # Execute the job and save the result to disk
            # Repeat until graceful_shutdown
            (question, state, job_id, data, question_data, category_data, min_questions, max_questions, command) = self.jobs_queue.get()
            if command == 'states_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.states_mean_solve(question, data), file)
            elif command == 'state_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.state_mean_solve(question, state, data), file)
            elif command == 'best5':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.best5_solve(question, data, min_questions, max_questions), file)
            elif command == 'worst5':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.worst5_solve(question, data, min_questions, max_questions), file)
            elif command == 'global_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.global_mean_solve(question, question_data), file)
            elif command == 'diff_from_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.diff_from_mean_solve(question, data, question_data), file)
            elif command == 'state_diff_from_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.state_diff_from_mean_solve(question, data, question_data, state), file)
            elif command == 'mean_by_category':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.mean_by_category_solve(question, category_data), file)
            elif command == 'state_mean_by_category':
                with open('results/job_id_' + str(job_id) + '.json', 'w') as file:
                    json.dump(self.state_mean_by_category_solve(question, category_data, state), file)