# auto-email-homework-fetcher

Connect to a POP3 server, check every email, and if a mail matches a rule, download and organize its attachments.

## Known Issues

 * Attachments with the same name overwrites each other
 * No strict checking and error recovering, may encounter encoding bugs
 * Not very many options (if you want to change something, tweak the code yourself -- it is only 90 lines)
 * No security concerns (e.g. all attachments will be downloaded without checking MIME type); use under your own risk and don't open any malicious file

## Configuration

Pretty straightforward: rename `config-example.ini` to `config.ini`, add a new section for your project, fill the rules then enable them in `config/tasks`.

## Usage

Run `fetch.py`.

## Requirements

 * Python 3

## Author

 * [James Swineson](https://swineson.me)

## Thanks

 * Fan Yang

## License

This piece of software is licensed under [DBAD Public License Version 1](http://www.dbad-license.org/). It is provided "AS IS" and is not guaranteed to work, and the author cannot be held reliable for any bugs, fireflies, data loss, system corruption, argument, divorce, atomic bomb, etc. caused or powered by this project.
