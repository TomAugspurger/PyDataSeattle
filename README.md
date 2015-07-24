Pandas .head() to .tail()
=========================

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/TomAugspurger/PyDataSeattle?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[http://tinyurl.com/sea-phtt](http://tinyurl.com/sea-phtt)

Should I Attend?
================

I'm targeting an experience level somewhere between novice and intermediate.
Hopefully you're familiar with the IPython notebook, and have heard of pandas.
If not, don't worry. The first two notebooks (~20 minutes) are for people who
may be entirely new to NumPy and pandas.

If you're more experienced, the first 30-40 minutes of the talk will likely be a review
for you. After that we'll get into some more advanced topics.

Setup
=====

First clone this repository

```bash
git clone https://github.com/tomaugspurger/pydataseattle
cd pydataseattle
```

- [git for windows](https://msysgit.github.io)
- `brew install git` on mac with [homebrew](http://brew.sh)

If that fails, try the [zip](https://github.com/TomAugspurger/PyDataSeattle/archive/master.zip).
It will probably be best to do a `git pull` just before the tutorial starts.

## Environment

Make sure that you're in the `pydataseattle` folder.

With conda:

```bash
conda update --all
conda env create -f environment.yml
source activate sea  # or activate sea on Windows
pip install beautifulsoup4
pip install simplejson
pip install vincent
```

With pip / virtualenv:

```bash
$ [sudo] pip install virtualenv  # try without sudo first
$ virtualenv --python=`which python3` sea
$ source sea/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt
```
Verify your installation with

```bash
python check_environment.py
```


Chat
====

I have no idea if this is useful, but we have a
[chat room](https://gitter.im/TomAugspurger/PyDataSeattle) for the tutorial.
If you have them, you can log in with your GitHub credentials.

Speak up in there with installation problems / questions / random gifs
if you find that more convenient.


Contents
========

- [Basics](notebooks/Basics.ipynb)
- [Operations](notebooks/operations.ipynb)
