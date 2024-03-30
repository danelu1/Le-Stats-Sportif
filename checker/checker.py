import requests
import json
import unittest

from datetime import datetime, timedelta
from time import sleep
import os

from deepdiff import DeepDiff

total_score = 0

ONLY_LAST = False

class TestAPI(unittest.TestCase):
    def setUp(self):
        os.system("rm -rf results/*")

    def check_res_timeout(self, res_callable, ref_result, timeout_sec, poll_interval = 0.2):
        initial_timestamp = datetime.now()
        while True:
            response = res_callable()
            # print(response)
        
            # Asserting that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)
        
            # Asserting the response data
            response_data = response.json()
            # print(f"Response_data\n{response_data}")
            if response_data['status'] == 'done':
                # print(f"Response data {response_data['data']} and type {type(response_data['data'])}")
                # print(f"Ref data {ref_result} and type {type(ref_result)}")
                d = DeepDiff(response_data['data'], ref_result, math_epsilon=0.01)
                self.assertTrue(d == {}, str(d))
                break
            elif response_data['status'] == 'running':
                current_timestamp = datetime.now()
                time_delta = current_timestamp - initial_timestamp
                if time_delta.seconds > timeout_sec:
                    self.fail("Operation timedout")
                else:
                    sleep(poll_interval)

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_states_mean(self):
        self.helper_test_endpoint("states_mean")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_state_mean(self):
        self.helper_test_endpoint("state_mean")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_best5(self):
        self.helper_test_endpoint("best5")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_worst5(self):
        self.helper_test_endpoint("worst5")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_global_mean(self):
        self.helper_test_endpoint("global_mean")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_diff_from_mean(self):
        self.helper_test_endpoint("diff_from_mean")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_state_diff_from_mean(self):
        self.helper_test_endpoint("state_diff_from_mean")

    @unittest.skipIf(ONLY_LAST, "Checking only the last added test")
    def test_mean_by_category(self):
        self.helper_test_endpoint("mean_by_category")

    def test_state_mean_by_category(self):
        self.helper_test_endpoint("state_mean_by_category")

    def helper_test_endpoint(self, endpoint):
        global total_score

        output_dir = f"tests/{endpoint}/output/"
        input_dir = f"tests/{endpoint}/input/"
        input_files = os.listdir(input_dir)

        test_suite_score = 10
        test_score = test_suite_score / len(input_files)
        local_score = 0

        for input_file in input_files:
            # Get the index from in-idx.json
            # The idx is between a dash (-) and a dot (.)
            idx = input_file.split('-')[1]
            idx = int(idx.split('.')[0])

            with open(f"{input_dir}/{input_file}", "r") as fin:
                # Data to be sent in the POST request
                req_data = json.load(fin)

            with open(f"{output_dir}/out-{idx}.json", "r") as fout:
                ref_result = json.load(fout)
            
            with self.subTest():
                # Sending a POST request to the Flask endpoint
                res = requests.post(f"http://127.0.0.1:5000/api/{endpoint}", json=req_data)

                job_id = res.json()
                # print(f'job-res is {job_id}')
                job_id = job_id["job_id"]

                self.check_res_timeout(
                    res_callable = lambda: requests.get(f"http://127.0.0.1:5000/api/get_results/{job_id}"),
                    ref_result = ref_result,
                    timeout_sec = 1)
                
                local_score += test_score
        total_score += min(round(local_score), test_suite_score)

if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        print(f"Total score {total_score}")
