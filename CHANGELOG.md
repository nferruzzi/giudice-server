# Giudice server - Change Log

The format is based on [Keep a Changelog](http://keepachangelog.com/en/0.3.0/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased

## [1.1.3] - 2018-04-27
### Changed
- use cherrypy to server requests (previously was the single threaded dev server from bottle)
- serial lock: 20 sec (was unlimited)
- sqlite lock: 15 sec
- ui refresh rate: 1.5 sec (was 1.0)

## [1.1.2] - 2018-04-24
### Added
- option to display converted results from 0..1 to 0..1000

## [1.1.1] - 2017-05-04
### Added
- report: ask to include for min/max vote

## [1.1.0] - 2017-04-19
### Added
- max vote, previous default was 100 now it's 10. Bump DB from 2 to 3
- alt plus: increase font
- alt minus: decrease font
- auto send votes to display

### Fixed
- report: dump all users
- ui: support from 0 to nUsers included

### Changed
- report trials: replace min and max values with '-'
- increase trials limit to 10

## [1.0.1] - 2016-04-24
### First public release
- Payload sub fetch