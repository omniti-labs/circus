# Circus - API client for circonus

Circus is a python based client for working with the circonus API. It allows
you to perform actions in bulk that may be difficult to perform using the web
UI. In addition to this, it has a templating system to allow you to create
checks and graphs based on json templates.

## Quick start

 * Clone the circus repository.
 * Go to https://circonus.com/user/tokens
 * Click the + button to generate a new token and set permissions for the new
   token.
 * Store the token in ~/.circusrc:

        [general]
        default_account=MyAccount
        
        [tokens]
        MyAccount=e4e6fe5f-8548-485b-9789-4e112ea1689f

 * `MyAccount` can be anything you choose and is just a name to help you
   identify the account.
 * Run the client with a simple test comand:

        ./circus list_accounts

 * You will get an error saying that the token needs to be validated.
 * Refresh the API token webpage and click the Allow Access button that should
   now be showing.
 * Run the client again with the test command:

        ./circus list_accounts

 * It should now be working correctly and show you a list of accounts.
 * Run `./circus help` for a list of commands and what they do.

## System wide installation

 * sudo ./setup.py install.
 * run 'circus' to run the client.

## Optional configuration

### Multiple circonus accounts

 * Set up tokens as above in the quick start section, but every time you run
   circus, add the `-a` option to specify the account you want to use.
 * The name of the account is determined by what you put before the token in
   the config file. For example:

        [tokens]
        foo=e4e6fe5f-8548-485b-9789-4e112ea1689f
        bar=7a918b10-f481-4d84-b47d-500e57a4afa8

 * If you had the configuration above, you would use `-a foo` or `-a bar` to
   work on the different accounts.
 * The `default_account` option specifies which account to use if you don't
   specify `-a`.

## User template directory

 * You can set an option in the `general` section of your `~/.circusrc` file
   called `template_dir`. This directory can contain custom templates that you
   create for adding checks, graphs etc.
 * Templates are stored in subdirectories under this directory based on their
   type. So for example, if you had `template_dir` set to
   `/home/foo/mytemplates` then you would put graph templates inside
   `/home/foo/mytemplates/graph`.
