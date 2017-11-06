## Data-Pipeline
App for processing DICOM MRI images and contour files. This is a command line app which:
  - processes source data directory (reconciles link.csv with actual dirs/files)
  - submits tasks into queue for parallel processing

###Notes

#### Parallelism/randomness:
To break down and run app in parallel on separate chunks of data we will utilize Celery.

For this demo, as unit of work (Celery task), we define a "per-patient" batch of files (all files related to one patient)

This means that each Celery worker will process only files related to a specific patient (list of dicom-contour  files). All celery workers can work in parallel on different patients. We can further breakdown tasks info smaller Celery tasks if needed (if patient data is too large for a single worker)

We can manage `randomness` via task queue configs, such that each worker can grab items out of the queue in a random order (FIFO is default). We can restrict certain tasks to run on specific workers if needed (ex: if you need to isolate certain patient datasets to run on specific hardware).


####Questions/Assumptions:

Not sure what params in dcm file define width/height. Looking up dcm images in gimp, it looks like dcm.rows/columns is width, height params.

In this demo we are working with local filesystem and passing filesystem paths to tasks for further processing. In production we will add some sort of cloud-based management layer (to load files from AWS for example)


### Installing dependencies:

- `pip install requirements.txt`

- HACK: unpack zip file into 'final_data' (normally we would pull data from AWS bucket, but for this demo we're just doing filesystem)

- HACK: install `runner app into 'dist-packages'

in this demo I will omit turning `runner` repo into a PIP installable app. Since celery tasks must be shared between both `runner` and `data-pipeline` projects, its best to install `runner` app into `dist-packages`

ex: after cloning `runner` repo run `sudo ln -s runner /usr/local/lib/python2.7/dist-packages/runner` (Note: adjust for your Virtualenv if needed)


### Running:

`python main.py -d final_data`
