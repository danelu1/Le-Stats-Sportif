from app import webserver
from flask import request, jsonify

import os
import json

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
    else:
        # Method Not Allowed
        return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    print(f"JobID is {job_id}")
    # TODO
    # Check if job_id is valid
    jid = job_id.split("_")[2]
    if not int(jid) < webserver.job_counter:
        return jsonify({
            'status': 'error',
            'reason': 'Invalid job_id'
            })
    else:
        file_name = 'results/job_id_' + jid + '.json'
        if os.path.exists(file_name):
            with open (file_name, 'r') as file:
                file_data = json.load(file)
                return jsonify({
                    'status': 'done',
                    'data': file_data
                })
        else:
            return jsonify({
                'status': 'running',
            })

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    # Get request data
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'states_mean'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data['state'],
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'state_mean'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'best5'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    data = request.json
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'worst5'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'global_mean'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'diff_from_mean'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'state_diff_from_mean'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
#     # TODO
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'mean_by_category'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
#     # TODO
    data = request.json
    print(f"Got request {data}")
    
    job_id = webserver.job_counter
    webserver.tasks_runner.jobs_queue.put((data["question"],
                                           data["state"] if "state" in data.keys() else None,
                                           job_id,
                                           webserver.data_ingestor.data,
                                           webserver.data_ingestor.helper(data["question"]),
                                           webserver.data_ingestor.data_by_category,
                                           webserver.data_ingestor.questions_best_is_min,
                                           webserver.data_ingestor.questions_best_is_max,
                                           'state_mean_by_category'))
    webserver.job_counter += 1

    return jsonify({"job_id": "job_id_" + str(job_id)})

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
