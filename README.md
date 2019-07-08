# braintrust


NPM commands

These were taken from the original documentation https://developer.webex.com/docs/sdks/browser
Do not do these anymore, start with npm install since package.json and package-lock.json already exist

This asks some questions and creates package.json
npm init

This command installs webex and adds it to package.json
Note: --save is depracated, do not use the option anymore,
    by default dependencies are saved to package.json
    (both save this under production section)
npm install --save webex

This command installs browserify and adds it to package.json,
     under the developer dependencies section
npm install --save-dev browserify

This command installs everything from package-lock.json, if present
Else the newest versions and deps of package-json
npm install

This command installs httpster globally
npm install -g httpster

