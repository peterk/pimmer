# pimmer
Exploratory code for PDF image mining. A multi page PDF will be split and converted to jpeg files that are mined for illustrations and images. Baed on https://github.com/megloff1/image-mining with added PDF splitting, a simple GUI and queue management.

## Install

Copy the example_env file to `.env` and edit settings.

Make sure you have a folder called `data` in the project root folder (jobs and resulting image files will end up here). You can map output to a different local folder for the worker in `docker-compose.yml`.

Run `docker-compose up`. Wait a minute until the queue and worker is up.

The service is now running on http://0.0.0.0:7777 . 


## Example result
A digitized hat catalog like this:
![Hat catalog page](testdata/hat_catalog_page.jpg?raw=true "Hat catalog page")

... can result in all the individual hat images:
![Individual hat images](testdata/hat_catalog_result.jpg?raw=true "Detected hat images")


