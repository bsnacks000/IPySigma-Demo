# IPySigma-Demo
#### current version: 0.1.2

This is a demo version of the IPySigma jupyter/node.js application for graph visualization.

IPySigma is a lightweight python package coupled with a node-express/socket.io app. It is designed to support a seamless workflow for graph visualization in jupyter notebook by using the jupyterlab/services javscript library to leverage communication between networkx objects and sigma.js. 

## Manual Install:
`git clone` this repo and install both the python and node components.


### Python

The prototype python package is contained in the `ipysig` folder.

1. From the root directory: Build and activate a clean python environment>=2.7.10 with requirements.txt using `virtualenv`.

2. `pip install -r requirements.txt` to get the required packages.

### Node.js

The node-express application is contained in the app folder.

1. Make sure your node version is >= v6.9.4 and that both `npm` and `bower` are installed globally.

2. From the root directory: `cd ./app`

3. type `npm install` to install the node modules locally in the `app` top-level folder

4. From `app`: `cd ./browser`

5. type `bower install` to install the bower_components folder (note: these steps might change in future versions with browserify)

## Run the Demo

1. At the root directory launch a jupyter notebook server and run the notebook `ipysig_test.ipynb`

2. Follow the instructions for each cell :)


