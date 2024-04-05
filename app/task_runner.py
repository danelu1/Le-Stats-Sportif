'''
Module used to process all the received tasks from the webserver through
the 'POST' methods. It uses the ThreadPool class to create a pool of threads
that will process the tasks. The tasks are processed by the TaskRunner class
in the run method.
'''

from queue import Queue
from threading import Thread, Event
import os
import json

class ThreadPool:
    '''
    Class used to create a pool of threads that will process the tasks
    received from the webserver. The number of threads is set by the
    TP_NUM_OF_THREADS environment variable. If it is not set, the number
    of threads will be the number of CPUs available on the computer.
    The threadpool contains a queue used to store all the received tasks.
    It also has an 'Event' used to shutdown the threadpool the moment
    the 'graceful_shutdown' method from the 'routes' module is called.
    '''
    def __init__(self):
        if 'TP_NUM_OF_THREADS' in os.environ:
            self.num_threads = int(os.environ['TP_NUM_OF_THREADS'])
        else:
            self.num_threads = os.cpu_count()

        self.jobs_queue = Queue()
        self.shutdown = Event()

        if not os.path.exists('results'):
            os.makedirs('results')

    def start(self):
        '''
        Method used to start the threadpool by starting
        a number of 'num_threads' threads.
        '''
        for _ in range(self.num_threads):
            TaskRunner(self).start()

    def join(self):
        '''
        Method used to join all the threads the moment
        the threadpool has been shutdown.
        '''
        if self.shutdown.is_set():
            for _ in range(self.num_threads):
                TaskRunner(self).join()

class TaskRunner(Thread):
    '''
    Class used to process all the tasks received from the webserver.
    The class receives the threadpool as parameter and uses to retrieve
    the tasks from the queue.
    '''
    def __init__(self, pool):
        super().__init__()
        self.thread_pool = pool

    def states_mean_solve(self, question, data):
        '''
        Method used to solve the 'states_mean' endpoint. It receives
        the question and all the necessary data extracted from the csv
        and computes the mean for each state that has the question.
        The method returns a sorted dictionary representing the solution.
        '''
        characteristics = data.items()
        stats = {state: sum(numbers) / len(numbers)
                for ((q, state), numbers) in characteristics
                if q == question and len(numbers) != 0}
        sorted_stats = sorted(stats.items(), key=lambda x: x[1])
        return dict(sorted_stats)

    def state_mean_solve(self, question, state, data):
        '''
        Method used to solve the 'state_mean' endpoint. It receives
        the question, the state and all the necessary data extracted
        from the csv and computes the mean for the state that has the
        question. The method returns a dictionary representing the solution.
        '''
        return {state: sum(data[(question, state)]) / len(data[(question, state)])}

    def best5_solve(self, question, data, min_questions, max_questions):
        '''
        Method used to solve the 'best5' endpoint. It receives the question,
        the data and the lists of questions from 'data_ingestor.py' and returns
        a dictionary containing the 5 states with the best mean for the question.
        '''
        if question in min_questions:
            return dict(list(self.states_mean_solve(question, data).items())[:5])
        if question in max_questions:
            return dict(list(self.states_mean_solve(question, data).items())[-5:])

    def worst5_solve(self, question, data, min_questions, max_questions):
        '''
        Same as best5, but returns the 5 states with the worst mean this time.
        '''
        if question in min_questions:
            return dict(list(self.states_mean_solve(question, data).items())[-5:])
        if question in max_questions:
            return dict(list(self.states_mean_solve(question, data).items())[:5])

    def global_mean_solve(self, data):
        '''
        Method used to compute the mean of all the values from the data
        processed in 'data_ingestor.py'.
        '''
        mean = sum([sum(x) for x in data.values()]) / sum([len(x) for x in data.values()])
        return {"global_mean": mean}

    def diff_from_mean_solve(self, question, data, question_data):
        '''
        Method used to compute the difference between the global mean
        and each state mean for a certain question.
        '''
        global_mean = self.global_mean_solve(question_data)["global_mean"]
        return {state: global_mean - self.state_mean_solve(question, state, data)[state]
                for (q, state) in data.keys() if q == question}

    def state_diff_from_mean_solve(self, question, data, question_data, state):
        '''
        Method used to compute the difference between the global mean
        and the given state mean for a given question.
        '''
        return {state: self.global_mean_solve(question_data)["global_mean"]
                - self.state_mean_solve(question, state, data)[state]}

    def mean_by_category_solve(self, question, category_data):
        '''
        Method used to compute the mean for each tuple of the form:
        (state, category, category_value). The method extracts those
        tuples from the given data that correspond to the given question
        and computes the mean for each tuple. It returns the result as
        a sorted dictionary.
        '''
        data_by_category = {x: numbers for (x, numbers) in category_data.items()
                            if x[0] == question and x[2] != '' and x[3] != ''}
        result = {str((x[1], x[2], x[3])):
            sum(data_by_category[x]) / len(data_by_category[x])
            for x in data_by_category.keys()}

        return dict(sorted(result.items(), key=lambda x: x[0]))

    def state_mean_by_category_solve(self, question, category_data, state):
        '''
        Same as the method above but this time the computations are made for
        a certain state and the result is a dictionary with the key being the
        given state and the value being another dictionary with the last 2
        characterstics written as tuples and representing the key and the 
        value being the mean for that tuple.
        '''
        data_by_category = {x: numbers for (x, numbers) in category_data.items()
                            if x[0] == question and x[1] == state
                            and x[2] != '' and x[3] != ''}

        result = {str((x[2], x[3])):
            sum(data_by_category[x]) / len(data_by_category[x])
            for x in data_by_category.keys()}

        return {state: dict(sorted(result.items(), key=lambda x: x[0]))}

    def run(self):
        '''
        Method used to process all the tasks received from the webserver.
        In an infinite loop it first checks if the threadpool has been
        shutdown through the 'graceful_shutdown' method and all the tasks
        have been processed(to break the loop and close the threadpool).
        If there are more jobs to process, they are retrieved and checked
        to see what function from the ones above should be used, depending
        on the command received. The result is written in a file.
        '''
        while True:
            if self.thread_pool.shutdown.is_set() and self.thread_pool.jobs_queue.empty():
                break

            (question, state, job_id, data_ingestor, command) = self.thread_pool.jobs_queue.get()
            if command == 'states_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.states_mean_solve(question,
                                                    data_ingestor.data), file)
            elif command == 'state_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.state_mean_solve(question,
                                                    state,
                                                    data_ingestor.data), file)
            elif command == 'best5':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.best5_solve(question,
                                            data_ingestor.data,
                                            data_ingestor.questions_best_is_min,
                                            data_ingestor.questions_best_is_max), file)
            elif command == 'worst5':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.worst5_solve(question,
                                                data_ingestor.data,
                                                data_ingestor.questions_best_is_min,
                                                data_ingestor.questions_best_is_max), file)
            elif command == 'global_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.global_mean_solve(data_ingestor.helper(question)), file)
            elif command == 'diff_from_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.diff_from_mean_solve(question,
                                                        data_ingestor.data,
                                                        data_ingestor.helper(question)), file)
            elif command == 'state_diff_from_mean':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.state_diff_from_mean_solve(question,
                                                            data_ingestor.data,
                                                            data_ingestor.helper(question),
                                                            state), file)
            elif command == 'mean_by_category':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.mean_by_category_solve(question,
                                                        data_ingestor.data_by_category), file)
            elif command == 'state_mean_by_category':
                with open('results/job_id_' + str(job_id) + '.json', 'w', encoding='utf-8') as file:
                    json.dump(self.state_mean_by_category_solve(question,
                                                                data_ingestor.data_by_category,
                                                                state), file)
