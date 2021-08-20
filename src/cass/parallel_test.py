import dispy, socket, os

curr_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = curr_dir + "/generated_test"

def unittest(f, test_dir):
    import os, socket, time
    error_dir = test_dir + "/" + "error_log"
    log_dir = test_dir + "/" + "standard_log"
    error_fname = error_dir + "/" + f.replace(".py", ".log")
    standard_fname = log_dir + "/" + f.replace(".py", ".log")
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
#    os.system("python " + test_dir + "/" + f + " 1> " + standard_fname + " 2> " + error_fname)
    os.system("python " + test_dir + "/" + f + " 1> " + error_fname + " 2> " + standard_fname)

    host = socket.gethostname()
    return (host, str(f))

if __name__ == '__main__':

    clusters = dispy.JobCluster(unittest)
    jobs = []

    files = os.listdir(test_dir)
    i = 0

#    host, f = unittest("unitTest_cass_SimpleQueryTest_testRangeTombstones_upgrade_test.py")
#    print('%s, %s',(host,f))


    for f in files:
        if f.find(".py") != -1:
            i += 1
            # schedule execution of 'compute' on a node (running 'dispynode')
            # with a parameter (random number in this case)
            job = clusters.submit(f, test_dir)
            job.id = i # optionally associate an ID to job (if needed later)
            jobs.append(job)
            # cluster.wait() # waits for all scheduled jobs to finish
    for job in jobs:
        print(job.id)
        host, f = job() # waits for job to finish and returns results
        print('%s executed job %s at %s, to execute %s' % (host, job.id, job.start_time, f))
        # other fields of 'job' that may be useful:
        # print(job.stdout, job.stderr, job.exception, job.ip_addr, job.start_time, job.end_time)
    clusters.print_status()
