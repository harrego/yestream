# yestream

Ye updates from multiple sources

![Preview image](https://raw.githubusercontent.com/harrego/yestream/main/preview.png)

## Privacy & Transparency

No identifiable user data is stored. Only messages, attachments and links within a message are stored in the database. The data stored is intentionally minimal and chosen with privacy in mind. All IDs are scrubbed before database entry and the only message origin data saved is the plain text transient channel and guild names it originated from.

All messages not from the specified channels are not logged or saved anywhere and are entirely discarded. When a message is received in one of the specified channels the following the data is saved in the database:

### Message

|Data Stored|Reason|
|-|-|
|Random ID|To identify the message in the database and find child attachments. This is not the Discord issued ID, this is generated on the fly only for the database.|
|Date the message was sent|To display alongside a message.|
|Text contents|To display on the web page.|
|Guild name|To display on the web page, not currently used but may be used in the future upon further testing. To be clear: this is not the ID, only the transient name in plain text.|
|Text channel name|To display on the web page, not currently used but may be used in the future upon further testing. Just like the guild name, this is not the ID, only the transient name in plain text.|
|All attachments|To display alongside a message, more details can be found below.|

### Attachment

If a message in a specified channel contains attachments, the following data from an attachment are stored in the database:

|Data Stored|Reason|
|-|-|
|Random ID|To identify the message in the database. This is not the Discord issued ID, this is generated on the fly only for the database.|
|File contents|To display alongside a message.|
|File name|To, if not an image, display alongside a message and retain the original name of the sent file for downloading.|
|File size|To display alongside the file name for downloading.|
|Database ID of the parent message.|To allow queries to find child attachments of a message to display alongside a message.|

### Link

If a link is included in the message then the link is scraped, the following data is stored in the database:

|Data Stored|Reason|
|-|-|
|URL|To query data for a link included in a message.|
|Date|Date that the information for the link was obtained. Currently unused but helpful for debugging.|
|Title|Site provided title of the webpage, used to display alongside a message including the source link.|
|Description|Site provided description of the webpage, used to display along a message include the source link.|

### Tweet

If a tweet is linked in the message, and the Twitter API is enabled, the following data is stored in the database:

|Data Stored|Reason|
|-|-|
|Twitter assigned tweet ID|To be able to re-call tweets in the database from messages and link to tweets when displayed on page.|
|Tweet date|To display on page alongside a tweet.|
|Tweet text contents|To display the tweet alongside a message.|
|Tweet poster's username|To display alongside the tweet and link to a tweet or user.|
|Tweet poster's display name|To display alongside the tweet.|

### Config

The following config data is saved in memory at initial run in order to determine the origin of a message:

|Data Stored|Reason|
|-|-|
|Channel IDs|Used to determine where a message is from and if it should be saved. As mentioned above the channel ID of a message is never saved in the database.|

## Infrastructure

`yestream` is a web app built in Python 3, it picks up updates from Discord channels, and displays them on a live webpage.

To make this happen it hosts a Discord self bot which waits for messages in specified channels, when a message is received it saves a re-assigned message ID, text contents, date sent, guild name, channel name and any attachments. The user who sent the message is not ever stored, neither is any message not from inside the specified channels. If a tweet is attached, and the Twitter API is enabled, the tweet data is saved in the database too.

Alongside the bot, a web app is hosted which is backed by the message database. Upon page load a template is used to display a specific amount of the most recent messages in the database. In each cell on the page the message contents, the date received and any attachments or tweets are displayed.

## Hosting a custom instance

### Discord Self-bot Warning

Running a Discord self-bot is a ToS violation, **hosting `yestream` will get your Discord account suspended, you've been warned.**

### Environment Variables

|Variable|Description|Required|
|-|-|-|
|`DISCORD_TOKEN`|Discord self-bot token extracted from the browser.|Yes|
|`DISCORD_CHANS`|Comma separated list of Discord channel IDs, e.g. `123456789,987654321`|Yes|

#### Twitter

Twitter API access is needed for the tweet preview alongside messages but it not required for the web app itself and can be skipped at the cost of the tweet previews.

|Variable|Required|
|-|-|
|`TWITTER_CONSUMER_KEY`|No|
|`TWITTER_CONSUMER_SECRET`|No|
|`TWITTER_ACCESS_TOKEN_KEY`|No|
|`TWITTER_ACCESS_TOKEN_SECRET`|No|

### Setup

1. Accept that running a self-bot is a Discord ToS violation and you will lose your Discord account.
2. Install `pipenv` through your package manager or `pip`.
3. Setup the `pipenv` environment: `pipenv install`.
4. Set the required environment variables at a minimum (above).
5. Run `pipenv run python3 main.py`.

### Docker Setup

1. Accept that running a self-bot is a Discord ToS violation and you will lose your Discord account.
2. Build the Docker image: `docker build -t harrego/yestream .`
3. Configure the port and environment variables accordingly and start the container. `/static` and `db.sqlite3` will be mapped to the local directory to persist data between containers: `docker run -d --restart unless-stopped -v $PWD/static:/app/static -v $PWD/db.sqlite3:/app/db.sqlite3 -p 3000:3000 -e PORT=3000 -e DISCORD_TOKEN=[discord token] -e DISCORD_CHANS=[discord channels] harrego/yestream`

### Custom theme

You can change the header, theme and pinned messages by editing `templates/index.html` and `assets/style.css`.