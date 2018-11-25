# pimmer
Exploratory code for PDF image mining. A multi page PDF will be split and converted to jpeg files that are mined for illustrations and images. Baed on https://github.com/megloff1/image-mining with added PDF splitting, a simple GUI and queue management.

## Install

1. Make sure you have Git and [Docker](https://www.docker.com) with docker-compose installed.
2. Get the latest version of this repository: `git clone --depth 1 https://github.com/peterk/pimmer.git`.
2. Copy the example_env file to `.env` and edit settings.
3. Make sure you have a folder called `data` in the project root folder (jobs and resulting image files will end up here). You can map output to a different local folder for the worker in `docker-compose.yml`.
4. Run `docker-compose up -d`. Wait a minute until the queue and worker is up.

The service is now running on http://0.0.0.0:7777.

If you are planning on processing a large number of documents you can start more workers with `docker-compose up -d --scale worker=5`.

Please report bugs and feedback in the Github issue tracker.

## Example result
A digitized hat catalog like this:
![Hat catalog page](testdata/hat_catalog_page.jpg?raw=true "Hat catalog page")

... can result in all the individual hat images:
![Individual hat images](testdata/hat_catalog_result.jpg?raw=true "Detected hat images")
