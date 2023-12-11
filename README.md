Moethread
=======================================
## Table of Contents

 * [Overview](#overview)
 * [Library Installalion](#library-installalion)
 * [Library Usage](#library-usage)


## Overview
Moethread is a python wrapper for the **ThreadPoolExecutor** library to easily multithread resource bound tasks. The library offers a decorator style of parallelizing
function calls.
**NOTE**, this only works for resource bound (API calls, network requests, disk read/write operations, etc) operations. If your task is **CPU** intensive, then this library may not offer much benefit and you're better off exploring other options such as **multiporcessing**.


## Library Installalion
To install the library simply run the following command in a cmd, shell or whatever...

```bash
# Windows
pip install moethread

# Linux
pip3 install moethread
```

## Library usage?
To start, you need to import the library

```python
from moethread import parallel_call

```

If you need to read results back from the parallelized function, then you have to define the internal variables/objects globally where you can
access them outside of that function. The function to parallelize will accept arguments and keyword arguments.
Arguments are primitives/constants/variables that you'd like to pass through to your function. If you'd like to have **counters** inside the parallelized function, then define those globally as shown in the following code snippet.
```python
global counter
counter = 0
```


As for the data which needs to be parallelized, this needs to be specified in the keywords argument. The keyword **data** is reserved for the input data.
The input data is a dictionary collection of whatever needs to run in parallel.

For example if you have a dataset of images and you would like to read those images in parallel and those images have labels, then you have to create a dictionary of image paths and their corrosponding labels. You have to make sure that the two lists are aligned.

```python
image_paths  = ["image_0.jpg", "image_1.jpg", ...] 	# some dummy paths
image_labels = [0, 1, ...] 		                # some dummy labels
assert len(image_paths) == len(image_labels)

# It's your responsiblity to ensure that elements align, e.g. image_labels[0] is the label for image_paths[0]
data = {"image_path": image_paths, "image_label": image_labels}
```

The next step is write the building block of your function. You will add the decorator **@parallel_call** on top of the function and assign **\*args and \*\*kwargs**
as your function parameters. Inside the function, you will read the data dictionary which contains the path to image and its corrosponding label.

```python

@parallel_call # decorator
def function_to_parallelize(*args, **kwargs):
	# Define globals...
	global counter
	# Read data in...
	image_path  = kwargs.get('data').get('image_path')
	image_label = kwargs.get('data').get('image_label')
	# Read image
	image = cv2.imread(image_path)
	if image_label == 1:
		counter += 1 # assume images with label == 1 are valid images
	## Do whatever you like to do below...

```

Lastly, you will just call the function and specify the number of threads. If you set threads = -1, then the libary will figure out the suitable number of threads for the task.

```python
function_to_parallelize(data=data, threads=-1) # automatically assigns the needed number of threads...
```

Putting it all together.

```python
from moethread import parallel_call

image_paths  = ["image_0.jpg", "image_1.jpg", ...] 	# some paths
image_labels = [0, 1, ...] 		                # some dummy labels
assert len(image_paths) == len(image_labels)

# It's your responsiblity to ensure that elements align, e.g. image_labels[0] is the label for image_paths[0]
data = {"image_path": image_paths, "image_label": image_labels}
global counter
counter = 0

@parallel_call # decorator
def function_to_parallelize(*args, **kwargs):
	# Define globals...
	global counter
	# Read data in...
	image_path  = kwargs.get('data').get('image_path')
	image_label = kwargs.get('data').get('image_label')
	# Read image
	image = cv2.imread(image_path)
	if image_label == 1:
		counter += 1 # assume images with label == 1 are valid images
	## Do whatever you like to do below...

function_to_parallelize(data=data, threads=-1) # Automatically assigns the needed number of threads...
```

### Another example, Pull-request processing.
This examples shows how to read github pull requests and parse body content and return a list of github users who produced failed pull-requests.

```python
from moethread import parallel_call

global invalid_pulls
github_users  = []
invalid_pulls = 0
github_token = ghx_test124
etag   = None
params = {'state': 'open'}
pulls  = list(self._iter(int(-1), url, repo.pulls.ShortPullRequest, params, etag))
@parallel_call
def process_pulls(*args, **kwargs):
    global invalid_pulls
    pull = kwargs.get('data').get('pulls')
    response = self._get(f'{url}/{pull.number}/reviews', auth=('', github_token))
    if response.ok:
        reviews = json.loads(response.text)
        for review in reviews:
            body = review.get('body', '').lower()
            err = "failure"
            if err in body:
                res = self._get(pull.user.url, auth=('', github_token))
                if res.ok:
                    github_user = json.loads(res.text)
                    github_users.append(github_user.get('login', ''))
                invalid_pulls += 1
                break
    elif response.status_code != 404:
        pass
process_pulls(data={"pulls": pulls}, threads=-1)

```

## Ready to go functions
The library is packed with some ready to go functions that can be used to perform several operations using `parallel_call` without having to write code. All you have to do is to call those functions.
- mtdo()
- mtdo_from_json()
- mtdo_from_csv()

```python
def mtdo(....)
	"""
	Performs a multithreaded data operation.

	Args:
		src_dir (str): source directory containing data to copy.
		dst_dir (str): destination directory to copy data to.
		op (str): operation type [cp: copy, mv: move, rm: delete, ren: rename].
		file_type (str, optional): type of data to copy, e.g '*.json' - copies json files only. Defaults to all data types '*.*'.
		sep_folder (str, optional): separation folder where right side directory structure is appended to destination directory,
									e.g. app/data/src/files, sep_folder='data', dest path -> os.path.join(dest_dir, 'src/files'). Defaults to ''.
		overwrite (bool, optional): whether to overwrite data in destination or skip already copied data on later trials. Defaults to False.
		prefix (str): prefix for image renaming, e.g prefix=data and image_name=im.jpg --> data_im.jpg
		threads (int, optional): number of threads to launch. Defaults to 8.
		**kwargs: Extra keywords such as (chunk_size: split data into equal sized chunks, verbose: supress moethread stdout), defaults to (chunk_size=5000, verbose=True)
	"""
```

```python
def mtdo_from_json(....)
	"""Performs a multithreaded data operation for paths in json file.

	Args:
		file_path (str): input json file containing paths
		data_key (str): dictionary key holding file paths
		label_key (str): (optional) dictionary key holding labels for folders name to copy/move data to (classifying copied/moved data based on labels)
		op (str): operation type [cp: copy, mv: move].
		threads (int, optional): number of threads to launch. Defaults to 8.
		**kwargs: Extra keywords such as (chunk_size: split data into equal sized chunks, verbose: supress moethread stdout), defaults to (chunk_size=5000, verbose=True)
	"""
```

```python
def mtdo_from_csv(....)
	"""Performs a multithreaded data operation for paths in csv file.

	Args:
		file_path (str): input json file containing paths
		data_key (str): dictionary key holding file paths
		label_key (str): (optional) dictionary key holding labels for folders name to copy/move data to (classifying copied/moved data based on labels)
		op (str): operation type [cp: copy, mv: move].
		threads (int, optional): number of threads to launch. Defaults to 8.
		**kwargs: Extra keywords such as (chunk_size: split data into equal sized chunks, verbose: supress moethread stdout), defaults to (chunk_size=5000, verbose=True)
	"""
```

----------------------------------------
Author: Hamdan, Muhammad (@mhamdan91 - ©)
