import importlib

packages = ['pandas', 'IPython', 'statsmodels', 'sklearn', 'seaborn',
            'toolz', 'bs4', 'requests', 'scipy', 'tables']

bad = []
for package in packages:
    try:
        importlib.import_module(package)
    except ImportError:
        bad.append("Can't import %s" % package)
else:
    if len(bad) > 0:
        print('\n'.join(bad))
    else:
        from sklearn.datasets import california_housing
        print("Caching california_housing")
        data = california_housing.fetch_california_housing()
        print("All good. Enjoy the tutorial!")

