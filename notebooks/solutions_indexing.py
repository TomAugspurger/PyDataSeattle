# Find the IPAs
is_ipa = df.beer_style.str.contains('IPA')
df[is_ipa]

# Find a subset of beer styles
df[(df.beer_style == 'American IPA') | (df.beer_style == 'Pilsner')].head()

# High Marks
# Long way:
df[(df.review_appearance >= 4) &
   (df.review_aroma >= 4) &
   (df.review_overall >= 4) &
   (df.review_palate >= 4) &
   (df.review_taste >= 4)]

# Short way
all_good = (df[review_cols] >= 4).all(1)
df[all_good].head()

# Pretty Good
df[df[review_cols].mean(1) >= 4].head()

# Top Beers
top_beers = reviews.index.get_level_values('beer_id').value_counts().head(10).index
reviews.loc[pd.IndexSlice[:, top_beers], ['beer_name', 'beer_style']]

