# UCEBlocker

The new and improved version of [miklosakos/fuck-uceprotect](https://github.com/miklosakos/fuck-uceprotect).

This Python script aims to block all incoming and outgoing emails from and to UCEProtect customers.

## What is UCEProtect?

UCEProtect is a DNS blacklisting provider, similar to Spamhaus, Spamcop, etc. but operates in a different way: extorts email server admins and organizations in order to get their IP address(es) unlisted from their services. This behavior is unacceptable, since major providers (Google, Microsoft) allows free blacklisting removal by filling out a simple form.

Originally this project was started out as a script made out of pure frustration and rage, has not been touched for approximately for four years and decided to refactor it, make it somewhat better!

## How to use

It's cool and all but how **do I** use it?

It's simple, you have everything in the repository you need, however you need to prepare your Postfix installation to make use of the script's new files.

Example Postfix configuration inside `main.cf`:

```
smtpd_sender_restrictions = ... check_sender_access hash:/etc/postfix/uceblocker/senders check_sender_access hash:/etc/postfix/uceblocker/sponsors_sender check_sender_access hash:/etc/postfix/uceblocker/trap_users_sender ...
smtpd_recipient_restrictions = ... check_recipient_access hash:/etc/postfix/uceblocker/recipients check_recipient_access hash:/etc/postfix/uceblocker/sponsors_recipient check_recipient_access hash:/etc/postfix/uceblocker/trap_users_recipient ...
virtual_alias_maps = ... hash:/etc/postfix/uceblocker/sensors ...
```

If you want to automatically update the lists and make postfix re-read the files you can setup an unprivileged user that has only access to the script and Postfix's `postmap` command.

An example `/etc/sudoers.d/uceblocker` file has been provided as part of the repository for privilege elevation.

An example `/var/spool/cron/crontab/uceblocker` file has been provided as part of the repository for automation.

You can configure the script using the provided `config.ini` file.

By default in the `[Extra]` section both UCEProtect sponsors and trap users are exempted from the blocks, change these to `True` if you want to block sending and receiving mails from them.

You can whitelist domains in the `[Exceptions]` section as a comma separated list, for example:
```
domains = test.tld,internal.test.tld,nobody.reads.this.lol
```

All rejection messages can be customized as long as Postfix file formatting is respected.