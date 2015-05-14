### Installing as an upstart job

*Tested on Ubuntu 14.04*

```
cp celeryd /etc/init.d/
cp celeryd_default /etc/default/celeryd
```

Modify paths in your /etc/default/celeryd as needed

```
chmod 700 /etc/init.d/celeryd
update-rc.d celeryd defaults
update-rc.d enable
```
