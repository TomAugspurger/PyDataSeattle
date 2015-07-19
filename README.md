Pandas .head() to .tail()
=========================

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/TomAugspurger/PyDataSeattle?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[http://tinyurl.com/sea-phtt](http://tinyurl.com/sea-phtt)

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
```

With pip / virtualenv:

```bash
$ [sudo] pip install virtualenv  # try without sudo first
$ virtualenv --python=`which python3` sea
$ source sea/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt
```

Contents
========

- [Basics](notebooks/Basics.ipynb)
- [Operations](notebooks/operations.ipynb)
