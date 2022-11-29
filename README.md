deploy instructions:

- [login to athena](https://sipb.mit.edu/doc/using-athena/)
- [sign up for scripts](https://scripts.mit.edu/web/)
  - if you're hosting this out of your own locker (`kerberos.scripts.mit.edu`) then you want to sign up your personal athena account
- [ssh into scripts](https://scripts.mit.edu/faq/41/can-i-ssh-to-scripts.mit.edu-to-test-my-scripts)
  - you'll be dropped in `~/web_scripts`
  - **every command below should be while sshed into scripts, not into athena**
- make a folder called `iap-backend`, clone this repo
  - `mkdir iap-backend`
  - `git clone https://github.com/cjquines/iap.git`
  - `cd iap`
- in the new folder, make a `deploy.sh` or some other script that updates it, with contents probably

  ```
  cd ~/web_scripts/iap-backend/iap
  rm -rf ./_events/*
  python3 scrape.py
  bundle exec jekyll build
  ```
- set `deploy.sh` to be executable and test it
  - `chmod +x deploy.sh`
  - `./deploy.sh`
  - go to `kerberos.scripts.mit.edu/iap-backend/iap/_site`, should be visible
  - in theory you can now run `./deploy.sh` to update, and then point people to your url
- get a better url by making a symlink
  - `cd ~/web_scripts`
  - `ln -s iap-backend/iap/_site iap`
  - go to `kerberos.scripts.mit.edu/iap`, should be visible
- run `./deploy.sh` automatically by editing a crontab
  - first, give scripts permission [to write data](https://scripts.mit.edu/faq/31/can-my-scripts-write-data-somewhere)
    - `cd ~/web_scripts/iap-backend/iap`
    - `athrun scripts fssar daemon.scripts write`
  - then, [edit your crontab](https://scripts.mit.edu/faq/30/how-do-i-list-my-current-crontab-how-do-i-remove-my-crontab)
    - `crontab -e`
    - add the entry `0 * * 12,1 * /afs/athena.mit.edu/user/k/e/kerberos/web_scripts/iap-backend/iap/deploy.sh`
    - (or whatever absolute path, use `pwd` to check)
    - (or whatever [cron schedule expression](https://crontab.guru/), this one is "every hour in december and january")
  - make sure to test this, this is fragile!
