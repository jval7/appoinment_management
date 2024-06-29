# Thirds party apis

## wsp:

1. https://medium.com/@rishicentury/how-to-use-whatsapp-cloud-api-6c4b4a22fc34

## Openai json mode:

1. https://platform.openai.com/docs/guides/text-generation/json-mode

## Google Calendar
1. https://developers.google.com/calendar/api/quickstart/python?hl=es-419
2. create events: https://developers.google.com/calendar/api/guides/create-events?hl=es-419#python

# Create lambda layer

run:

1. create a temporal folder
2. `pip install -r requirements.txt --platform=manylinux2014_x86_64 --only-binary=:all: --target ./python/lib/python3.11/site-packages/`
3. `zip -r layer.zip python`

