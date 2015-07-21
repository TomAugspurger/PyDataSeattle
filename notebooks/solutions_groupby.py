(df.groupby(df.text.str.len())
   .review_overall
   .mean()
   .plot(style='.k', figsize=(10, 5)))

# question
avg = (df.groupby(['brewer_id', 'beer_name'])
       .review_overall
       .mean())
extrema = avg.groupby(level='brewer_id').agg(['min', 'max'])
difference = extrema['max'] - extrema['min']
difference.order(ascending=False)


# Find the `beer_style` with the greatest variance in `abv`.
df.groupby('beer_style').abv.std().order(ascending=False)
