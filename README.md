# Alfred Web Button Workflow

A simple Alfred workflow to manage and quickly access your web bookmarks/buttons.

## Features

- Add web buttons with custom names and tags
- Search buttons by name or tags
- Quick access to your favorite websites
- Simple and intuitive interface

## Installation

1. Download the latest release from the [releases page](https://github.com/schwark/alfred-webbutton/releases)
2. Double click the `.alfredworkflow` file to install
3. Alfred will automatically install the workflow

## Usage

The workflow uses the `wb` keyword to access all functionality.

### Adding a Web Button

```
wb add name|url|tag1,tag2
```

Example:
```
wb add GitHub|https://github.com|dev,code
```

### Accessing Web Buttons

Simply type `wb` followed by your search term. The workflow will search through button names and tags.

Example:
```
wb github
```

### Search by Tags

Include tags in your search to filter buttons by their tags:

```
wb dev
```

## Development

This workflow is built using Python and the [Alfred-Workflow](https://github.com/deanishe/alfred-workflow) library.

To contribute:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License

# alfred-aadvantageshopping
Alfred  Workflow for to access AAdvantage Eshopping sites 
## Install

* Download .workflow file from [Releases](https://github.com/schwark/alfred-aadvantageshopping/releases)
* Can be installed from Packal at http://www.packal.org/workflow/aadvantage-eshopping
* Can also be downloaded from github as a zip file, unzip the downloaded zip, cd into the zip directory, and create a new zip with all the files in that folder, and then renamed to AAdvantageshopping.alfredworkflow
* Or you can use the workflow-build script in the folder, using
```
chmod +x workflow-build
./workflow-build . 
```

## Store Update

```
aeconfig update
```
This should be needed once at the install, and everytime you want to update promotional cashback information - the links to the stores are the same, but the subtitle data with cashback information may be dated if this is not run regularly

## Logo Update

```
aeconfig logos
```
This should be needed once at the install, and everytime you want to update store logos

## Show Stores and Links

```
ae [:fav|:prm] <query>
```
This will allow you to search for any store - and will show matching stores as well as the cashback information. If a store is running a promotional elevated cashback, it will be denoted by a 🏆 symbol, and will shows the regular cashback information as well. Favorite stores are denoted by ❤️

Clicking takes you directly to the site, assuming you are logged into https://aadvantageeshopping.com, else you will be prompted to login before you go to site

Shift clicking an item sets it as a favorite store, or unsets as favorite

Adding :fav to the query will limit results to favorited stores

Adding :prm to the query will limit results to stores that have a promotional rebate level


## Reinitialize

```
aeconfig reinit
```
This should only be needed if you ever want to start again for whatever reason - removes all API keys, devices, scenes, etc.

## Update

```
aeconfig workflow:update
```
An update notification should show up when an update is available, but if not invoking this should update the workflow to latest version on github

## Acknowledgements
