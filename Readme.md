# Champions League Analytics

## Project Description
This project is a sports league database application that manages football teams, players, matches, and player statistics. It includes 8 clubs, 120 initial players, and 3 seasons. The statistics, match results, and transfers are sample data and are not official UEFA records.

## Tools Used
- Python
- Tkinter
- PostgreSQL
- pgAdmin 4
- psycopg2

## Features
- League standings and player rankings
- Player search and match results
- Season comparisons and performance reports
- Coaches, stadiums, contracts, injuries, and transfers
- Add, update, and delete player records

## Relational Schema
PK = primary key; FK = foreign key.

- teams: team_id (PK), team_name, country, founded_year
- players: player_id (PK), player_name, nationality, position, birth_date
- coaches: coach_id (PK), coach_name, nationality, team_id (FK)
- seasons: season_id (PK), season_name, start_date, end_date
- venues: venue_id (PK), venue_name, city, country, capacity
- games: game_id (PK), season_id (FK), home_team_id (FK), away_team_id (FK), venue_id (FK), game_date, home_score, away_score
- player_statistics: stat_id (PK), player_id (FK), game_id (FK), team_id (FK), goals, assists, minutes_played, yellow_cards, red_cards
- contracts: contract_id (PK), player_id (FK), team_id (FK), start_date, end_date, annual_salary
- injuries: injury_id (PK), player_id (FK), injury_type, injury_date, recovery_date
- transfers: transfer_id (PK), player_id (FK), from_team_id (FK), to_team_id (FK), transfer_date, transfer_fee

## Normalization
The base tables are designed toward third normal form (3NF). Each field stores a single value, records have primary keys, and related information is separated into tables connected by foreign keys. This reduces repeated information.

## Advanced SQL
The project uses joins, aggregate functions, subqueries, views, indexes, a stored procedure, and ranking window functions. The league_standings and player_rankings views display analytical results. The current-season ranking includes selected illustrative statistics rather than a complete match-derived leaderboard.

## How to Run
1. Install Python and PostgreSQL.
2. Create a PostgreSQL database named champions_league and restore the project database SQL export.
3. Install the Python driver: `python -m pip install psycopg2-binary`.
4. Check the database host, port, and username in Main.py.
5. Run `python Main.py` and enter your PostgreSQL password.

The application opens directly to the dashboard.
