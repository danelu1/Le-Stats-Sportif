Name: Bogdan-Andrei Sprîncenatu
Group: 332CC

Organization:
The homework consisted of a server which received requests through some given routes and
processed them to get statistics about the lifestyle of americans between 2011 and 2022
based on a given "csv" file.

I chose to solve the homework by considering all the needed characteristics for a "Threadpool"
and a "TaskRunner" thread(for which I give the whole "Threadpool" as parameter in the constructor
to have the queue and the event for each job processing) and then add each request posted on the
server in the queue(responsible with the jobs), through the "treat_route" function, as long as the
server has not received a "graceful shutdown". Here, I also increment the "job_counter" to give
each task an associated id. This can be seen through the following piece of code:

if not server.tasks_runner.shutdown.is_set(): # The server did not receive a shutdown
    # I keep adding all the characteristics needed for solving the request
    server.tasks_runner.jobs_queue.put((data["question"], data["state"] if "state" in data.keys() else None, job_id, server.data_ingestor, route.split("/")[2]))
    # Increment the counter for future requests.
    server.job_counter += 1

The "run()" function of the "TaskRunner" class checks if the server finished to process all the
remained tasks in the queue after the shutdown, through the following piece of code:

if self.thread_pool.shutdown.is_set() and self.thread_pool.jobs_queue.empty():

and it breaks the infinite loop when this happens(it means that we can now close the "Threadpool").
Otherwise the loop continues and for each iteration, a new job is retrieved from the queue and
checked to see its type. For each type of route I have a function which solves the given request
and writes the output in "json" format to a file with the name of the form "job_id_{number}", in
the "results" directory. I didn't need to use any synchronization mechanisms(like locks or barriers),
the queue being itself synchronized(similar to the "BlockingQueue" from Java), and so no busy waiting
was used in this homework.

I consider this homework to be very useful for the fact that you learn how REST API and Python
multithreading work by solving the requests posted to the server through a "Threadpool".

I consider my implementation efficient, the only overhead being the one caused by the "csv"
reading and the "category" tasks where I have to sort the final result(so O(n * log(n))
time complexity, where "n" is the size of the final result, which is smaller than the size
of the initial data), so I don't really know other way which could improve the complexity
of my solution(but I would be glad to know if there is a more efficient one).

Implementation:
I implemented all the sections of the homework, including the logging and the unittests and I
also tested the last 3 requested "GET" routes to check if they work properly.

The main dificulty of the homework consisted in understanding how the server works and where do
I have to do all the computations needed to solve the effective tasks. Once I realized that the
"routes" module is used for adding the requests in the "Threadpool" and the "TaskRunner" class
is used to solve them, the homework was done in a few hours.

Resources:
Main resources used for solving the homework:
https://docs.python.org/3/library/os.html
https://docs.python.org/3/library/csv.html
https://docs.python.org/3/howto/logging.html

Git:
https://github.com/danelu1/Le-Stats-Sportif
