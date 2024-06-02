<img src="https://github.com/sofagasbuddy/sofagasbuddy-scraper/raw/main/app_logo.png"  width="200" height="200">

# SOFAGasBuddy-Scraper
Scraper for the AAFES ESSO program, that presents the relevant data as an API or a simple web page

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/SOFAGasBuddy/SOFAGasBuddy-Scraper/.github%2Fworkflows%2Fdocker-publish.yml)

## Usage
First, clone the repo to a directory of choice

`git clone https://github.com/SOFAGasBuddy/SOFAGasBuddy-Scraper`

The bot needs two environment variables set to work

* SSN - The social security number of someone on the ESSO account, no spaces or dashed: `123456789`
* VRN - The plate number of an active vehicle on the account, exactly as it appears (including a space): `S XX1234`, `KL H765`, etc...

The data can be accessed at 5 API endpoints

* `/` - Returns the ESSO card balance, plus all the info about the currently active vehicles as JSON
* `/html` - Same as above, but as a simple HTML table that can either be imbedded into a dashboard or easily referenced
* `/all` - Same as `/`, but shows all previous vehicles associated with the account
* `/all/html` - Same as `/all`, but as an HTML table
* `/balance` - Returns only the current balance, as JSON

### Docker
Preferred method is with docker. You can use the pre-built docker container on ghcr.io or build your own with the included `Dockerfile`.

#### docker compose
Set the appropriate environment variables in the `docker-compose.yml` file.


`docker-compose up -d` or `docker compose up -d` depending on your version of docker.

The container should be running on port 9999, accessable via the above mentioned API endpoints.

#### docker
`docker run -d -p 9999:9999 -e SSN="123456789 -e VRN="S RF9999" --restart unless-stopped --name essoscraper ghcr.io/sofagasbuddy/sofagasbuddy-scraper:main`

Replace SSN and VRN with your information

#### native Python

The bot can be run as native Python, but it is not recommended as it will be subject to the differences of your environment. Example below for a Linux environment.

`$ python -m venv .`

`$ source bin/activate`

`(venv)$ pip install -r requirements.txt`

`(venv)$ export SSN="123456789"`

`(venv)$ export VRN="S HH9999"`

`(venv)$ python ./main.py`

## Dashboard example

Take the following example out from a call to `/`

```json
{
  "0": {
    "availalble": "351.12",
    "exp_date": "17 Apr 2025",
    "limit": "400.00",
    "status": "Active",
    "type": "POV",
    "vrn": "S XX9999"
  },
  "1": {
    "availalble": "518.33",
    "exp_date": "12 Sep 2025",
    "limit": "600.00",
    "status": "Active",
    "type": "POV",
    "vrn": "S YY9999"
  },
  "balance": "$420.69"
}
```

In [Homepage](https://gethomepage.dev/latest/widgets/services/customapi/), you would add the following to your `services.yml` file where you wanted it to appear:

```yaml
- ESSOScraper:
    widget:
      type: customapi
      url: http://sofagasbuddyscraperhost:9999/
      method: GET
      mappings:
        - field: balance
          label: Balance
          format: text
        - field:
            0: available
          label: My Car
          suffix: L
          format: text
        - field:
            1: available
          label: Spouses Car
          suffix: L
          format: text
```
