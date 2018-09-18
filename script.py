import sys
import requests
import os
import json
from time import sleep

SUCCESS = 0
ERROR = 1
# Stop job if it runs more than TIME_LIMIT seconds (default value)
TIME_LIMIT = 600
# Interval for checking job status
TIME_INTERVAL = 1

# Check the number of command line arguments
args_given = len(sys.argv)
if args_given < 3 or args_given > 4:
    print('Usage: python script.py <job_file>.json <dcos_url> (<TIME_LIMIT>)')
    sys.exit(ERROR)

# Check if TIME_LIMIT was given as a command line argument
if args_given == 4:
    TIME_LIMIT = int(sys.argv[3])

print('TIME_LIMIT: ' + str(TIME_LIMIT))

# Parse the command line arguments
job_file = sys.argv[1]
print(job_file)
dcos_url = sys.argv[2]
print(dcos_url)

# Load json job data from job file
with open(job_file) as f:
    job_data = json.load(f)
print(job_data)

job_id = job_data['id']
print(job_id)

# Create the job
# jobs_url -> {dcos_url}/service/metronome/v1/jobs
jobs_url = '%s/service/metronome/v1/jobs' % (dcos_url,)
r = requests.post(jobs_url, json=job_data)
print('Create job: ' + str(r.status_code))

# Check if a job with the same id already exists
# In this case, should the existing job be updated?
if r.status_code != 201:
    print('A job with the same id already exists!')
    # sys.exit(ERROR)

# API url used for accesing information about the job
# job_url -> {dcos_url}/service/metronome/v1/jobs/{jobId}
job_url = '%s/%s' % (jobs_url, job_id)

# Run the job
# runs_url -> {dcos_url}/service/metronome/v1/jobs/{jobId}/runs
runs_url = '%s/runs' % (job_url,)
r = requests.post(runs_url)
print('Run job: ' + str(r.status_code))
# Get the run id
run_info = json.loads(r.text)
run_id = run_info['id']
print(run_id)

# API url used for getting information about the job run
# run_url -> {dcos_url}/service/metronome/v1/jobs/{jobId}/runs/{runId}
run_url = '%s/%s' % (runs_url, run_id)

# API url used for stopping the job run
# stop_url -> {dcos_url}/service/metronome/v1/jobs/{jobId}/runs/{runId}/actions/stop
stop_url = '%s/actions/stop' % (run_url,)

# API url used for getting the history information for the job
# history_url -> {dcos_url}/service/metronome/v1/jobs/{jobId}?embed=history
history_url = '%s?embed=history' % (job_url)

# Seconds waited for the job to finish
seconds_waited = 0

while True:
    # The job is taking too long to execute - stop it
    if seconds_waited >= TIME_LIMIT:
        r = requests.post(stop_url)
        print('Stop: ' + str(r.status_code))
        print('Job %s (runId: %s) takes too long to execute - job terminated!' % (job_id, run_id))
        sys.exit(ERROR)
    print(run_url)
    r = requests.get(run_url)
    print('Run info: ' + str(r.status_code))
    # Job is done, check history for status
    if r.status_code != 200:
        r = requests.get(history_url)
        print('History: ' + str(r.status_code))
        history = json.loads(r.text)['history']
        print(history)
        failed_runs = history['failedFinishedRuns']
        print('FAILED RUNS')
        print(failed_runs)
        # Check if the run was a failure
        for run in failed_runs:
            if run['id'] == run_id:
                print('Error at executing job %s (runId: %s)!' % (job_id, run_id))
                sys.exit(ERROR)
        # Job executed successfully
        print('Job %s (runId: %s) executed successfully!' % (job_id, run_id))
        sys.exit(SUCCESS)
    print(r.text)
    status_json = json.loads(r.text)
    status = status_json['status']
    print(status)
    # Something is wrong (is this check ok?)
    if status != 'ACTIVE' and status != 'INITIAL':
        print('Error at executing job %s (runId: %s)!' % (job_id, run_id))
        sys.exit(ERROR)
    # Wait TIME_INTERVAL seconds before checking the status again
    sleep(TIME_INTERVAL)
    seconds_waited = seconds_waited + TIME_INTERVAL
