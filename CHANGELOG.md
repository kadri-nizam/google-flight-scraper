# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Retry on StaleException

### Changed
- URL query is made to be more stable by removing unneeded data
- Rename variable to make code clearer
- Switch to using regex to get departure and arrival date
- Switch to provided flight duration as simply subtracting negates timezone shifts


## [0.1.0] - 2023-10-23

### Added
- Specified library's dependencies
- Added TravelPlan class to easily specify travel parameters
- Added FlightQuery class to easily construct the query URL
- Defined driver interface for easily specifying different web-drivers
- Added Scraper class to scrape queries
- Started ReadMe
