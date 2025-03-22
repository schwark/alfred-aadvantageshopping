# Alfred Mileage Rewards Shopping Workflow

A powerful Alfred workflow for quick access to Mileage Rewards Shopping. Search for stores, view rebate rates, and manage your favorites.

## Features

- 🔍 Quick search for stores
- 💰 View current rebate rates and bonus percentages
- ⚡ Highlight elevated rebate rates
- 🏷️ Show store categories
- ❤️ Favorite stores for quick access
- 🎯 Direct store access
- 📱 Mobile tracking support
- 🔄 Automatic store data updates
- 🎨 Brand-specific store logos
- 🔑 Support for multiple brands (AAdvantage, United, etc.)

## Usage

### Basic Search
1. Type `ae` followed by your search query
2. Results show:
   - Store name
   - Current rebate rate
   - Bonus percentage (if elevated)
   - Store categories
   - Favorite status
   - Mobile tracking availability

### Subtitle Emojis
- ❤️ - Store is in favorites
- 💰 - Regular rebate rate (e.g., "💰 2%")
- ⚡ - Elevated rebate rate (e.g., "⚡ 5% (+150% bonus)")
- 🏷️ - Store categories
- 🎯 - Direct store (no redirect)
- 📱 - Mobile tracking available

### Modifiers
When viewing search results, you can use these keyboard shortcuts to take actions on each store:
- `⇧` + `↵` - Toggle store as favorite (add/remove from favorites)
- `↵` - Open store in browser (requires login to aadvantageeshopping.com)

### Commands
- `ae update` - Force update store data
- `ae logos` - Update store logos
- `ae reinit` - Reinitialize workflow
- `ae brand <brand>` - Switch to different brand (e.g., `ae brand united`)

### Filters
- `:fav` - Show only favorite stores
- `:prm` - Show only stores with elevated rates

### Example Queries
- `ae amazon` - Search for Amazon
- `ae :fav` - Show all favorite stores
- `ae :prm` - Show all stores with elevated rates
- `ae :fav :prm` - Show favorite stores with elevated rates
- `ae walmart :prm` - Search for Walmart with elevated rates
- `ae target :fav` - Search for Target in favorites

## Installation

1. Download the [latest release](https://github.com/schwark/alfred-aadvantageshopping/releases/latest)
2. Double-click the `.alfredworkflow` file
3. Alfred will install the workflow

## License

MIT License. See LICENSE file for details.

## Multi-Brand Support

This workflow supports multiple shopping portals. When you switch brands:
- The workflow's name and icon change to match the selected brand
- Store rewards are shown in the brand's currency (e.g., AAdvantage miles, United miles, Delta SkyMiles)
- Your brand selection persists until you switch to a different brand

American Airlines is the default brand, but you can switch between brands using:

```
ae brand <brand>
```

Available brands:

| Brand | Command | Default | Currency |
|-------|---------|---------|----------|
| ![American Airlines](https://www.google.com/s2/favicons?domain=aa.com) American Airlines | `ae brand american` | ✓ | AAdvantage miles |
| ![United Airlines](https://www.google.com/s2/favicons?domain=united.com) United Airlines | `ae brand united` | | United miles |
| ![Delta Air Lines](https://www.google.com/s2/favicons?domain=delta.com) Delta Air Lines | `ae brand delta` | | Delta SkyMiles |
| ![Alaska Airlines](https://www.google.com/s2/favicons?domain=alaskaair.com) Alaska Airlines | `ae brand alaska` | | Alaska Mileage Plan miles |
| ![Southwest Airlines](https://www.google.com/s2/favicons?domain=southwest.com) Southwest Airlines | `ae brand southwest` | | Rapid Rewards points |
| ![USAA](https://www.google.com/s2/favicons?domain=usaa.com) USAA | `ae brand usaa` | | USAA points |
| ![Barclays](https://www.google.com/s2/favicons?domain=barclays.com) Barclays | `ae brand barclays` | | Barclays points |
