# calm-dsl-engine

Calm DSL Engine describes a simpler Python 3 based DSL for writing Calm blueprints.
Look at this [example](https://github.com/ideadevice/calm-dsl-engine/blob/master/tests/next_demo/test_next_demo.py) to see a blueprint in action.

## Dev Setup

Pre-Reqs for Mac:
 - Get python3 using brew - `brew install python3`
 - Install [Docker for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

Pre-Reqs for Centos:
 - `make _init_centos` to setup your CentOS 7 VM for development. This will install python3 and docker.

Use:
 -  `make dev` to create/use python3 virtualenv in `$TOPDIR/venv` and setup dev environment. Activate it by calling `source venv/bin/activate`. Use `deactivate` to deactivate virtualenv.
 -  `make test` to run the test cases.
 -  `make dist` to generate a `calm.dsl` python distribution.
 -  `make gui` to install jupyter notebook and extensions in your virtualenv.
 -  `make docker` to build docker container. (Assumes docker client is setup on your machine)
 -  `make run` to run container.
 -  `make clean` to reset.


Code formatted by [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## CLI Usage

Point the CLI to your Calm setup by using a config file, or command line args.

### Config file

 By default, the CLI looks for this information in `~/.calm/server/config.ini`.<br/>
 You can instruct it to look elsewhere by using the `--config` option to point to your config file:<br/>
 `calm --config=/home/my_dir/config.ini get bps`
 An example config is given at `server/config.ini`.

### Config overrides
 You can override any setup details by passing them in explicitly:<br/>
 `calm --ip=10.20.4.35 --port=9220 --username=custom_user --password=something ...[the rest of your command]`

### CLI Examples:

#### Create Blueprint:
 Run `calm create bp` to upload your DSL blueprint to Calm:
 `calm create bp --file path/to/your_bp.py`

 | Option  		    | Type 			    | Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | -f, --file  	  | File path  	  | Path of Blueprint file to upload  [Required]|
 | \-\-name  		  | Text          |	Blueprint name |
 | \-\-description | Text          |	Blueprint description            |

 Both relative and absolute paths are supported.

#### List Blueprints:
 `calm get bps` fetches blueprints on the Calm server.

 | Option  		    | Type     			| Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | \-\-name  		  | Text          |	Search for blueprints by name |
 | \-\-filter      | Text         |	Filter for blueprints. All Rest API filters are supported. |
 | \-\-limit       | Integer      |	Number of blueprints to fetch              |
 | \-\-offset      | Integer      |	Starting point of blueprints (for pagination)            |
 | -q, \-\-quiet   | Flag         |	Show only blueprint names              |
 | -a, \-\-all-items| Flag        |	Get all items, including deleted ones              |

 **Examples:**

 | Aim  		                       | Command	                                   |
 | ----------------------------    | --------------------------------------------|
 | Get blueprint named `MySQL`     | `calm get bps --name=MySQL`           |
 | Get blueprint in Active state   | `calm get bps --filter=state==ACTIVE` |
 | Get deleted blueprints          | `calm get bps --filter=state==DELETED` |
 | Get the third page of 20 blueprints | `calm get bps --offset=40 --limit=20` |

#### Launch Blueprint:
 `calm launch bp <blueprint name>` deploys a blueprint. The blueprint must exist on the Calm server.

 | Option  		    | Type     			| Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | \-\-app_name   | Text          |	Name of application to be created |

 **Example:**
  Launch blueprint `MySQL` as app named `Prod_DB`: <br/>
  `calm launch bp MySQL --app_name=Prod_DB`

#### Delete Blueprint:
 `calm delete bp <blueprint names>` deletes the blueprint(s) named. <br/>
 Multiple blueprints can be deleted by giving space separated names.

**Example:**
  Delete blueprint `MySQL1` and `Cassandra2`: <br/>
  `calm delete bp MySQL1 Cassandra2`

#### List Apps:
 `calm get apps` fetches applications on the Calm server.<br/>
 (Options are same as those for listing blueprints.)

 | Option  		    | Type     			| Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | \-\-name  		  | Text          |	Search for applications by name |
 | \-\-filter      | Text         |	Filter for applications. All Rest API filters are supported. |
 | \-\-limit       | Integer      |	Number of applications to fetch              |
 | \-\-offset      | Integer      |	Starting point of applications (for pagination)            |
 | -q, \-\-quiet   | Flag         |	Show only blueprint names              |
 | -a, \-\-all-items| Flag        |	Get all items, including deleted ones              |

#### Run Actions:
 `calm run action <action name> --app=<app name>` will trigger `action name` on application `app name`.

 | Option  		    | Type     			| Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | \-\-app  		  | Text          |	Application on which to run the action [Required] |
 | -w \-\-watch   | Flag          |	Watch scrolling output as the action executes. |

 **Example:**
  Run action `scale_out_by_1` on app `MySQL`: <br/>
  `calm run action scale_out_by_1 --app=MySQL`

#### Monitor Actions:
 `calm watch action_runlog <runlog_uuid> --app=<app name>` will poll on the action until it terminates.

 | Option  		    | Type     			| Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | \-\-app  		  | Text          |	Application where the action is running [Required] |
 | \-\-poll-interval | Integer    |	Specify polling interval (Default: 10 seconds) |

#### Monitor App:
 `calm watch app <app name>` will poll on the application until it is in a non-busy state.

 | Option  		    | Type     			| Description	                                |
 | -------------  | ------------- |---------------------------------------------|
 | \-\-app  		  | Text          |	Application to watch [Required] |
 | \-\-poll-interval | Integer    |	Specify polling interval (Default: 10 seconds) |




## Reference

 - [Doc](https://docs.google.com/document/d/1SVTDISGy-1gZdeSOMyONON4WP6iFpZGJkdVkB_lEeZs/edit)
