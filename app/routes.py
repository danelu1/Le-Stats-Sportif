'''
Module used to define the routes of the webserver and the functions that are
called when a request is made to a certain route.
'''
import os
import json
import copy
from flask import request, jsonify
from app import webserver

def treat_route(server, req, route):
    '''
    Function used to treat a certain route given as parameter.
    The given request is parsed and a new job_id is initialised
    for the new received job. The operations are made as long as
    the server did not receive the shutdown command(which closes
    the threadpool). The question, the state(if it exists), the
    new id, the data_ingestor object from __init__.py(which
    encapsulates all the data needed to do the computations) and
    the route name(the one after '/api/') are sent to the threadpool.
    The job_counter is incremented and the new job_id is returned.
    If the server is shutting down, an error message is returned.
    '''
    data = req.json

    server.logger.info(f"Received data: {data}")

    job_id = server.job_counter

    if not server.tasks_runner.shutdown.is_set():
        server.tasks_runner.jobs_queue.put((data["question"],
                                            data["state"] if "state" in data.keys() else None,
                                            job_id,
                                            server.data_ingestor,
                                            route.split("/")[2]))

        server.job_counter += 1

        server.logger.info(f"Added job with id: job_id_{job_id} to the queue")

        return jsonify({"job_id": "job_id_" + str(job_id)})

    return jsonify({"status": "error", "reason": "Server is shutting down"})

@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    '''
    Method used to treat the '/api/post_endpoint' route.
    '''
    if request.method == 'POST':
        data = request.json

        response = {"message": "Received data successfully", "data": data}

        return jsonify(response)

    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    '''
    Method used to get the status of a certain task, using
    the given 'job_id'. First, I extract the number from the
    'job_id_{number}' string and check if this number is smaller
    than the actual job_counter. If it isn't, than the given
    'job_id' is invalid and an error message is returned. If the
    'job_id' is valid, I check if the file 'results/job_id_{number}.json'
    exists and its size is different than 0(bigger, more precisely),
    because this way I can be sure that the task was processed and
    the computation were done and added to the file(I also check for
    the size of the file because there is a chance that the file is
    created but the task is not added in it, and so the thread did not
    have time to write the results in the file). In a contrary case, I
    simply return a message saying that the task is still running.
    '''
    jid = job_id.split("_")[2]
    if int(jid) >= webserver.job_counter:
        return jsonify({
            'status': 'error',
            'reason': 'Invalid job_id'
            })

    file_name = 'results/job_id_' + jid + '.json'
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
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
    '''
    Method used to treat the '/api/states_mean' route.
    '''
    return treat_route(webserver, request, "/api/states_mean")

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    '''
    Method used to treat the '/api/state_mean' route.
    '''
    return treat_route(webserver, request, "/api/state_mean")

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    '''
    Method used to treat the '/api/best5' route.
    '''
    return treat_route(webserver, request, "/api/best5")

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    '''
    Method used to treat the '/api/worst5' route.
    '''
    return treat_route(webserver, request, "/api/worst5")

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    '''
    Method used to treat the '/api/global_mean' route.
    '''
    return treat_route(webserver, request, "/api/global_mean")

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    '''
    Method used to treat the '/api/diff_from_mean' route.
    '''
    return treat_route(webserver, request, "/api/diff_from_mean")

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    '''
    Method used to treat the '/api/state_diff_from_mean' route.
    '''
    return treat_route(webserver, request, "/api/state_diff_from_mean")

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    '''
    Method used to treat the '/api/mean_by_category' route.
    '''
    return treat_route(webserver, request, "/api/mean_by_category")

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    '''
    Method used to treat the '/api/state_mean_by_category' route.
    '''
    return treat_route(webserver, request, "/api/state_mean_by_category")

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    '''
    Method used to shutdown the server gracefully by setting
    the event from the threadpool.
    '''
    webserver.tasks_runner.shutdown.set()
    return jsonify({"status": "ok"})

@webserver.route('/api/jobs', methods=['GET'])
def jobs():
    '''
    Method used to get the status of all the tasks from the
    queue. If the server is shutting down and the queue is empty,
    I return a message saying that there are no jobs. Contrary,
    I check if the file 'results/job_id_{number}.json' exists and
    its size is different than 0 and this way I can add a new task
    to the list.
    '''
    if webserver.tasks_runner.shutdown.is_set() and webserver.tasks_runner.jobs_queue.empty():
        return jsonify({'status': 'done', 'jobs': []})

    jobs_list = []
    q = copy.copy(webserver.tasks_runner.jobs_queue)
    while not q.empty():
        job = q.get()
        file_name = 'results/job_id_' + job[2] + '.json'
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            jobs_list.append({"job_id_" + job[2]: "done"})
        else:
            jobs_list.append({"job_id_" + job[2]: "running"})

    return jsonify({'status': 'done', 'jobs': jobs_list})

@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    '''
    Method used to get the number of jobs from the queue. If the server
    is shutting down(the threadpool actually), the queue size should be 0.
    '''
    if webserver.tasks_runner.shutdown.is_set() and webserver.tasks_runner.jobs_queue.empty():
        return jsonify({'status': 'done', 'num_jobs': 0})

    return jsonify({'status': 'running', "num_jobs": webserver.tasks_runner.jobs_queue.qsize()})

@webserver.route('/')
@webserver.route('/index')
def index():
    '''
    Method used to treat the '/' and '/index' routes.
    '''
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    paragraphs = ""
    for route in routes:
        paragraphs.join(f"<p>{route}</p>")

    msg += paragraphs
    return msg

def get_defined_routes():
    '''
    Method used to get all the defined routes from the webserver.
    '''
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
