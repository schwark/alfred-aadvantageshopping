# Alfred Mileage Rewards Shopping Search

An Alfred workflow to search and open Mileage Reward links to Shopping stores.

## Features

- Search stores by name
- Open store directly in browser
- Show current rebate percentage
- Show promotional status
- Show regular rebate percentage
- Filter by favorites
- Filter by promotional status
- Sort promotional results by bonus percentage
- Multi-brand support for various shopping portals

## Multi-Brand Support

This workflow now supports multiple shopping portals. American Airlines is the default brand, but you can switch between brands using:

```
ae brand <brand>
```

Available brands:

| Brand | Logo | Command | Default |
|-------|------|---------|---------|
| American Airlines | ![American Airlines](https://www.aa.com/favicon.ico) | `ae brand american` | ✓ |
| United Airlines | ![United Airlines](https://www.united.com/favicon.ico) | `ae brand united` | |
| Delta Air Lines | ![Delta Air Lines](https://www.delta.com/favicon.ico) | `ae brand delta` | |
| Alaska Airlines | ![Alaska Airlines](https://www.alaskaair.com/favicon.ico) | `ae brand alaska` | |
| Southwest Airlines | ![Southwest Airlines](https://www.southwest.com/favicon.ico) | `ae brand southwest` | |
| USAA | ![USAA](https://www.usaa.com/favicon.ico) | `ae brand usaa` | |
| Barclays | ![Barclays](https://www.barclays.com/favicon.ico) | `ae brand barclays` | |

## Usage

1. Type `ae` to start searching
2. Type store name to filter results
3. Use `:prm` to filter for promotional stores (sorted by bonus percentage)
4. Use `:fav` to filter for favorite stores
5. Press `Enter` to open store in browser
6. Press `⌘+Enter` to toggle favorite status

## Commands

- `ae update` - Update store data
- `ae logos` - Update store logos
- `ae reinit` - Reinitialize workflow
- `ae brand <brand>` - Set current brand
- `ae workflow:update` - Update workflow to latest version

## Installation

1. Download the [latest release](https://github.com/schwark/alfred-aadvantageshopping/releases/latest)
2. Double click to install in Alfred
3. Type `ae` to start using

## License

MIT License

## Store Update

```
ae update
```
This should be needed once at the install, and everytime you want to force update promotional cashback information - the links to the stores are the same, but this information should automatically update once a day - so you should never need to run this

## Logo Update

```
ae logos
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
ae reinit
```
This should only be needed if you ever want to start again for whatever reason - removes all API keys, devices, scenes, etc.

## Update

```
ae workflow:update
```
An update notification should show up when an update is available, but if not invoking this should update the workflow to latest version on github

## Acknowledgements
