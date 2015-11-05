About
=====

![robo-ph](robo-ph-cover_art.jpg)

Requirements
============

Python
------

* [PyObjC](http://pythonhosted.org/pyobjc/)
* [requests](http://docs.python-requests.org/en/latest/)
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)

If you have conda, install these with:

```
pip install pyobjc
conda install requests beautifulsoup4
```

if you don't have conda, install with:

```
pip install pyobjc requests beautifulsoup4
```


Other
-----

* [ffmpeg](http://ffmpeg.org/)
* [AtomicParsley](http://atomicparsley.sourceforge.net/)

If you have MacPorts, install these with:

```
sudo apt-get install atomicparsley ffmpeg
```

Running
=======

```
python generate.py
```