Get a value count matrix from two columns


```python
cat1 | cat2
---- | ----
c11  | c21
c11  | c22
c12  | c33
```

to

```
    c21 c22 c23 ...
c11 1   3   1
c12 0   12  1
c12 1   7   8
...
```

with

```python
cats.assign(cnt=1).groupby(['age', 'inc_hh_vb']).cnt.sum().unstack().fillna(0)
```

mmmm
.sub & .div\nGroupby.get_group
