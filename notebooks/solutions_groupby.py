(df.groupby(df.text.str.len())
   .review_overall
   .mean()
   .plot(style='.k', figsize=(10, 5)))

# min-max gap
avg = (df.groupby(['brewer_id', 'beer_name'])
       .review_overall
       .mean())
extrema = avg.groupby(level='brewer_id').agg(['min', 'max'])
difference = extrema['max'] - extrema['min']
difference.order(ascending=False)


# Find the `beer_style` with the greatest variance in `abv`.
df.groupby('beer_style').abv.std().order(ascending=False)

# Review by words
df.groupby(df.text.str.count('\w')).review_overall.mean().plot(style='k.')

# Review by sentences.
(df.groupby(df.text.str.count('[. |! |\? |; ]'))
    .review_overall
    .mean()
    .plot(style='k.'))

# kinds per brewer
beer_kind.groupby(df.brewer_id).nunique()

# brewer per kind
df.brewer_id.groupby(beer_kind).nunique()

# distinct brewers per day
x = df.set_index('time').brewer_id
x.resample('D', how='nunique').plot()
