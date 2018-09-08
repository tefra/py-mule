# py-mule
[![Build Status](https://travis-ci.org/tefra/py-mule.svg?branch=master)](https://travis-ci.org/tefra/py-mule)
[![codecov](https://codecov.io/gh/tefra/py-mule/branch/master/graph/badge.svg)](https://codecov.io/gh/tefra/py-mule)
![GitHub top language](https://img.shields.io/github/languages/top/tefra/py-mule.svg)

## History
The last interesting project I was involved with at my last workplace was called ***Mule***. It is responsible to retrieve and serve flight content from multiple providers as fast as possible. Mule was written in java8 with spring boot and webflux

## Goal
As I need to fresh up on my python and get a little familiar with django I decided to port as much of the mule to python3.

Tasks:
  - [x] Search endpointS
  - [x] Data classes and mappers
  - [x] Use ReactiveX to achieve concurrency and implement HTML SSE responses
  - [x] Caching
  - [ ] Redirect endpoints
  - [ ] Enhance resources with static resources
  - [ ] Cover subjects such as CORS, HTTP Auth, Configuration ...
  - [ ] Use content from dummy apis
  - [ ] Dockerization
  
  
## Installation

You need pyenv and pipenv

```bash
git clone git@github.com:tefra/py-mule.git mule
cd mule
pipenv install
python manage.py runserver

``` 
  
## Credits
  
@aggfeli
@kefthymiou
@tsompos
@cboursinos
@Enginehead
@kefthymiou
@eraikakou
@mylk
@tarvanitis

---

```
         __
   __   (__`\
  (__`\   \\`\
   `\\`\   \\ \
     `\\`\  \\ \
       `\\`\#\\ \#
         \_ ##\_ |##
         (___)(___)##
          (0)  (0)`\##
           |~   ~ , \##
           |      |  \##
           |     /\   \##         __..---'''''-.._.._
           |     | \   `\##  _.--'                _  `.
           Y     |  \    `##'                     \`\  \
          /      |   \                             | `\ \
         /_...___|    \                            |   `\\
        /        `.    |                          /      ##
       |          |    |                         /      ####
       |          |    |                        /       ####
       | () ()    |     \     |          |  _.-'         ##
       `.        .'      `._. |______..| |-'|
         `------'           | | | |    | || |
                            | | | |    | || |
                            | | | |    | || |
                            | | | |    | || |
                      _____ | | | |____| || |
            ci/revop /     `` |-`/     ` |` |
                     \________\__\_______\__\
                      """""""""   """""""'"""

```