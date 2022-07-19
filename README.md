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

## Show Stores and Links

```
ae [:fav|:prm] <query>
```
This will allow you to search for any store - and will show matching stores as well as the cashback information. If a store is running a promotional elevated cashback, it will be denoted by a 🏆 symbol, and will shows the regular cashback information as well. Favorite stores are denoted by ❤️

Shift clicking an item sets it as a favorite store.

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
