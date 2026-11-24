import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from getpass import getpass

# Database connection
conn = psycopg2.connect(host='localhost', database='champions_league',
                        user='postgres', password=getpass('PostgreSQL password: '),
                        port='5432')

root = tk.Tk()
root.title('Champions League Analytics')
root.geometry('1100x650')
root.configure(bg='#07143D')

# Run a query and display its results
def query(sql, values=()):
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
        if cursor.description:
            columns = [column.name for column in cursor.description]
            rows = cursor.fetchall()
        else:
            columns, rows = [], []
    conn.commit()
    return columns, rows


def show(title, sql, values=()):
    try:
        columns, rows = query(sql, values)
        heading.config(text=title)
        table.delete(*table.get_children())
        table['columns'] = columns
        short_names = {'games_played': 'Played', 'goal_difference': 'GD',
                       'goals_for': 'GF', 'goals_against': 'GA',
                       'player_rank': 'Rank', 'total_goals': 'Goals',
                       'total_assists': 'Assists', 'total_minutes': 'Minutes'}
        for column in columns:
            table.heading(column, text=short_names.get(column, column.replace('_', ' ').title()))
            if column.endswith('_name') or column in ('home_team', 'away_team'):
                table.column(column, width=175, minwidth=155, anchor='w')
            else:
                table.column(column, width=75, minwidth=65, anchor='center')
        for i, row in enumerate(rows):
            color = 'even' if i % 2 == 0 else 'odd'
            table.insert('', 'end', values=['' if x is None else x for x in row], tags=(color,))
        status.config(text=str(len(rows)) + ' records')
    except Exception as error:
        conn.rollback()
        messagebox.showerror('Database error', str(error))


def dashboard():
    show('Dashboard', '''SELECT 'Clubs' AS category, COUNT(1) AS total FROM teams
        UNION ALL SELECT 'Players', COUNT(1) FROM players
        UNION ALL SELECT 'Seasons', COUNT(1) FROM seasons
        UNION ALL SELECT 'Games', COUNT(1) FROM games
        UNION ALL SELECT 'Injuries', COUNT(1) FROM injuries
        UNION ALL SELECT 'Transfers', COUNT(1) FROM transfers''')


def standings():
    show('League Standings - Simulation', '''SELECT team_name, games_played,
        wins, draws, losses, goals_for, goals_against, goal_difference, points
        FROM league_standings WHERE season_name = %s
        ORDER BY points DESC, goal_difference DESC''', (season.get(),))


def rankings():
    show('Player Rankings - Sample Statistics', '''SELECT player_rank, player_name,
        team_name, total_goals, total_assists, total_minutes FROM player_rankings
        WHERE season_name = %s ORDER BY player_rank''', (season.get(),))


def players():
    show('Players', '''SELECT p.player_id, p.player_name, p.nationality,
        p.position, p.birth_date, t.team_name FROM players p
        LEFT JOIN contracts c ON p.player_id = c.player_id
        LEFT JOIN teams t ON c.team_id = t.team_id ORDER BY p.player_id''')


def search():
    name = simpledialog.askstring('Search', 'Enter player or club name:')
    if name is not None:
        show('Search Results', '''SELECT p.player_id, p.player_name, p.position,
            p.nationality, t.team_name FROM players p
            LEFT JOIN contracts c ON p.player_id = c.player_id
            LEFT JOIN teams t ON c.team_id = t.team_id
            WHERE p.player_name ILIKE %s OR t.team_name ILIKE %s
            ORDER BY p.player_name''', ('%' + name + '%', '%' + name + '%'))


def matches():
    show('Match Results - Simulation', '''SELECT g.game_id, g.game_date,
        h.team_name AS home_team, g.home_score, g.away_score,
        a.team_name AS away_team, v.venue_name FROM games g
        JOIN teams h ON g.home_team_id = h.team_id
        JOIN teams a ON g.away_team_id = a.team_id
        JOIN seasons s ON g.season_id = s.season_id
        LEFT JOIN venues v ON g.venue_id = v.venue_id
        WHERE s.season_name = %s ORDER BY g.game_date''', (season.get(),))


def comparison():
    show('Season Comparison - Simulation', '''SELECT team_name, season_name,
        games_played, wins, goals_for, points FROM league_standings
        ORDER BY team_name, season_name''')


def coaches():
    show('Coaches', '''SELECT t.team_name, c.coach_name, c.nationality
        FROM coaches c JOIN teams t ON c.team_id = t.team_id ORDER BY t.team_name''')


def venues():
    show('Stadiums', 'SELECT venue_name, city, country, capacity FROM venues ORDER BY venue_name')


def contracts():
    show('Contracts - Sample Data', '''SELECT p.player_name, t.team_name,
        c.start_date, c.end_date, c.annual_salary FROM contracts c
        JOIN players p ON c.player_id = p.player_id
        JOIN teams t ON c.team_id = t.team_id ORDER BY p.player_name''')


def injuries():
    show('Injuries - Sample Data', '''SELECT p.player_name, i.injury_type,
        i.injury_date, i.recovery_date FROM injuries i
        JOIN players p ON i.player_id = p.player_id ORDER BY i.injury_date DESC''')


def transfers():
    show('Transfers - Sample Data', '''SELECT p.player_name, f.team_name AS from_team,
        t.team_name AS to_team, x.transfer_date, x.transfer_fee FROM transfers x
        JOIN players p ON x.player_id = p.player_id
        JOIN teams f ON x.from_team_id = f.team_id
        JOIN teams t ON x.to_team_id = t.team_id ORDER BY x.transfer_date DESC''')


def report():
    show('Above Average Scorers - Sample Statistics', '''SELECT player_name,
        team_name, total_goals, total_assists FROM player_rankings
        WHERE season_name = %s AND total_goals > (SELECT AVG(total_goals)
        FROM player_rankings WHERE season_name = %s) ORDER BY total_goals DESC''',
        (season.get(), season.get()))


def save_player(update=False):
    player_id = None
    if update:
        player_id = simpledialog.askinteger('Update Player', 'Player ID:')
        if player_id is None:
            return
    name = simpledialog.askstring('Player', 'Player name:')
    if not name:
        return
    nationality = simpledialog.askstring('Player', 'Nationality:')
    if nationality is None:
        return
    position = simpledialog.askstring('Player', 'Position (Goalkeeper, Defender, Midfielder, Forward):')
    if position is None:
        return
    position = position.strip().title()
    if position not in ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']:
        messagebox.showerror('Invalid position', 'Enter one of the four listed positions.')
        return
    try:
        if update:
            with conn.cursor() as cursor:
                cursor.execute('UPDATE players SET player_name=%s, nationality=%s, position=%s WHERE player_id=%s',
                               (name, nationality, position, player_id))
                if cursor.rowcount == 0:
                    messagebox.showwarning('Not found', 'Player ID not found.')
                    conn.rollback()
                    return
        else:
            query('INSERT INTO players (player_name, nationality, position) VALUES (%s,%s,%s)',
                  (name, nationality, position))
        conn.commit()
        messagebox.showinfo('Success', 'Player saved.')
        players()
    except Exception as error:
        conn.rollback()
        messagebox.showerror('Error', str(error))


def delete_player():
    player_id = simpledialog.askinteger('Delete Player', 'Player ID:')
    if player_id is None or not messagebox.askyesno('Confirm', 'Delete this player?'):
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM players WHERE player_id=%s', (player_id,))
            removed = cursor.rowcount
        conn.commit()
        messagebox.showinfo('Delete', 'Player deleted.' if removed else 'Player ID not found.')
        players()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        messagebox.showwarning('Protected record', 'This player has related records. Delete a newly added test player instead.')
    except Exception as error:
        conn.rollback()
        messagebox.showerror('Error', str(error))


app = tk.Frame(root, bg='#07143D')
tk.Label(app, text='CHAMPIONS LEAGUE ANALYTICS', font=('Arial', 20, 'bold'), bg='#07143D', fg='white').pack(pady=12)
tk.Label(app, text='Simulated league data', bg='#07143D', fg='#B8C9FF').pack()
sidebar = tk.Frame(app, bg='#10265C')
sidebar.pack(side='left', fill='y', padx=8, pady=8)
content = tk.Frame(app, bg='#07143D')
content.pack(side='left', fill='both', expand=True, padx=8, pady=8)
season = tk.StringVar(value='2026/27')
tk.Label(content, text='Season (select before opening a report)', bg='#07143D', fg='white').pack()
ttk.Combobox(content, textvariable=season, values=['2024/25', '2025/26', '2026/27'], state='readonly').pack(pady=5)
heading = tk.Label(content, text='Dashboard', font=('Arial', 18, 'bold'), bg='#07143D', fg='white')
heading.pack(pady=8)
results = tk.Frame(content)
results.pack(fill='both', expand=True)
style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview', font=('Arial', 10), rowheight=26)
style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background='#193A80', foreground='white')
table = ttk.Treeview(results, show='headings')
table.tag_configure('even', background='#FFFFFF')
table.tag_configure('odd', background='#E5EDFF')
vertical = ttk.Scrollbar(results, orient='vertical', command=table.yview)
horizontal = ttk.Scrollbar(results, orient='horizontal', command=table.xview)
table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
vertical.pack(side='right', fill='y')
horizontal.pack(side='bottom', fill='x')
table.pack(fill='both', expand=True)
status = tk.Label(content, bg='#07143D', fg='white')
status.pack(pady=5)

buttons = [('Dashboard', dashboard), ('League Standings', standings),
           ('Player Rankings', rankings), ('All Players', players),
           ('Search Players', search), ('Match Results', matches),
           ('Season Comparison', comparison), ('Coaches', coaches),
           ('Stadiums', venues), ('Contracts', contracts), ('Injuries', injuries),
           ('Transfers', transfers), ('Performance Report', report),
           ('Add Player', save_player), ('Update Player', lambda: save_player(True)),
           ('Delete Player', delete_player), ('Exit', root.destroy)]
for label, action in buttons:
    tk.Button(sidebar, text=label, command=action, width=22, font=('Arial', 10),
              bg='#193A80', fg='white', relief='flat').pack(pady=1)

app.pack(fill='both', expand=True)
dashboard()
root.mainloop()
conn.close()
