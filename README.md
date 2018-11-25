# pimmer
Exploratory code for PDF image mining. A multi page PDF will be split and converted to jpeg files that are mined for illustrations and images. Baed on https://github.com/megloff1/image-mining with added PDF splitting, a simple GUI and queue management.

![Alt text](testdata/hat_catalog_page.jpg?raw=true "Title")
![Alt text](testdata/hat_catalog_result.jpg?raw=true "Title")

## Install

Copy the example_env file to .env and edit settings.

Make sure you have a folder called "data" in the project root folder (jobs and resulting image files will end up here).

Run docker-compose up -d

The service is now running on http://0.0.0.0:7777

