from app import webserver
from flask import request, jsonify
import os
import json

def treat_route(webserver, request, route):
    data = request.json
    
    job_id = webserver.job_counter
    
    if not webserver.tasks_runner.shutdown.is_set():
        webserver.tasks_runner.jobs_queue.put((data["question"],
                                            data["state"] if "state" in data.keys() else None,
                                            job_id,
                                            webserver.data_ingestor,
                                            route.split("/")[2]))
        webserver.tasks_runner.lock.acquire()
        webserver.job_counter += 1
        webserver.tasks_runner.lock.release()

        return jsonify({"job_id": "job_id_" + str(job_id)})
    
    return jsonify({"status": "error", "reason": "Server is shutting down"})

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json

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
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            try:
                with open(file_name, 'r') as file:
                    file_data = json.load(file)
                    return jsonify({
                        'status': 'done',
                        'data': file_data
                    })
            except json.JSONDecodeError:
                return jsonify({'status': 'error'})
        else:
            return jsonify({
                'status': 'running',
            })

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    # TODO
    return treat_route(webserver, request, "/api/states_mean")

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    # TODO
    return treat_route(webserver, request, "/api/state_mean")


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    # TODO
    return treat_route(webserver, request, "/api/best5")

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    # TODO
    return treat_route(webserver, request, "/api/worst5")

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    # TODO
    return treat_route(webserver, request, "/api/global_mean")

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    # TODO
    return treat_route(webserver, request, "/api/diff_from_mean")

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    # TODO
    return treat_route(webserver, request, "/api/state_diff_from_mean")

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    # TODO
    return treat_route(webserver, request, "/api/mean_by_category")

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    # TODO
    return treat_route(webserver, request, "/api/state_mean_by_category")

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    webserver.tasks_runner.shutdown.set()
    return jsonify({"status": "ok"})

@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    if webserver.tasks_runner.shutdown.is_set() and webserver.tasks_runner.jobs_queue.empty():
        return jsonify({'status': 'done', 'num_jobs': 0})
    
    return jsonify({'status': 'running', "num_jobs": webserver.tasks_runner.jobs_queue.qsize()})

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
