import unittest
import os
import json
import requests
import time
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool, TaskRunner

ONLY_LAST = False

class TestWebserver(unittest.TestCase):
    # def setUp(self):
    #     os.system("rm -rf results/*")
    
    task_runner = TaskRunner(ThreadPool())
    data_ingestor = DataIngestor("./unittests/test_table.csv")
    
    def retrieve_info(self, end_point):
        with open(f"unittests/tests/{end_point}/input/in-1.json", "r") as file:
            in_data = json.load(file)
            return in_data["question"], in_data["state"] if "state" in in_data else None
        
        return None
    
    def retrieve_output(self, end_point):
        with open(f"unittests/tests/{end_point}/output/out-1.json", "r") as file:
            return json.load(file)
        
        return None
    
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_states_mean(self):
        q, _ = self.retrieve_info("states_mean")
        result = self.task_runner.states_mean_solve(q, self.data_ingestor.data)
        ref = self.retrieve_output("states_mean")
        
        self.assertEqual(result, ref)
        
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_state_mean(self):
        q, state = self.retrieve_info("state_mean")
        result = self.task_runner.state_mean_solve(q, state, self.data_ingestor.data)
        ref = self.retrieve_output("state_mean")
        
        self.assertEqual(result, ref)
        
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_best5(self):
        q, _ = self.retrieve_info("best5")
        min_questions = self.data_ingestor.questions_best_is_min
        max_questions = self.data_ingestor.questions_best_is_max
        result = self.task_runner.best5_solve(q, self.data_ingestor.data, min_questions, max_questions)
        ref = self.retrieve_output("best5")
        
        self.assertEqual(result, ref)
        
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_worst5(self):
        q, _ = self.retrieve_info("worst5")
        min_questions = self.data_ingestor.questions_best_is_min
        max_questions = self.data_ingestor.questions_best_is_max
        result = self.task_runner.worst5_solve(q, self.data_ingestor.data, min_questions, max_questions)
        ref = self.retrieve_output("worst5")
        
        self.assertEqual(result, ref)
    
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_global_mean(self):
        result = self.task_runner.global_mean_solve(self.data_ingestor.data)
        ref = self.retrieve_output("global_mean")
        
        self.assertEqual(result, ref)
        
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_diff_from_mean(self):
        q, _ = self.retrieve_info("diff_from_mean")
        result = self.task_runner.diff_from_mean_solve(q, self.data_ingestor.data, self.data_ingestor.helper(q))
        ref = self.retrieve_output("diff_from_mean")
        
        self.assertEqual(result, ref)
        
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_state_diff_from_mean(self):
        q, state = self.retrieve_info("state_diff_from_mean")
        result = self.task_runner.state_diff_from_mean_solve(q, self.data_ingestor.data, self.data_ingestor.helper(q), state)
        ref = self.retrieve_output("state_diff_from_mean")
        
        self.assertEqual(result, ref)
        
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_mean_by_category(self):
        q, _ = self.retrieve_info("mean_by_category")
        result = self.task_runner.mean_by_category_solve(q, self.data_ingestor.data_by_category)
        ref = self.retrieve_output("mean_by_category")
        
        self.assertEqual(result, ref)
    
    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")    
    def test_state_mean_by_category(self):
        q, state = self.retrieve_info("state_mean_by_category")
        result = self.task_runner.state_mean_by_category_solve(q, self.data_ingestor.data_by_category, state)
        ref = self.retrieve_output("state_mean_by_category")
        
        self.assertEqual(result, ref)
        
if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        print("Total score: MAMA MEA")