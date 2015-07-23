# win indicator
games['home_win'] = games['home_points'] > games['away_points']
games.head()

# Wins per team
wins_as_away = games.groupby('away_team').home_win.agg(
    {'n_games': 'count', 'n_wins': lambda x: (~x).sum()}
)
wins_as_home = games.groupby('home_team').home_win.agg(
    {'n_games': 'count', 'n_wins': 'sum'}
)
wins = (wins_as_away + wins_as_home)
wins.head()

# Win percent
wins = (wins_as_away + wins_as_home)
strength = wins.n_wins / wins.n_games
strength.index.name = 'team'
strength.name = 'strength'

