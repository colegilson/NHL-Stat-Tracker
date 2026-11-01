# NHL Stat Tracking DataBase

## What is this?
This is a stat tracking database written in python, using SQL for database management, for the NHL's players for the 2026-2027 season! It was made using the official(?) NHL API ("https://api-web.nhle.com/v1"). Currently it will track player's: id(from the api), name, position, team, games_played, assists, goals, plus_minus, points, power_play_points, shots, shooting_percentage, goals_against_avg, losses, ot_losses, save_percentage, shutouts, and wins for players around the NHL!

## Why does this exist?
I grew up loving hockey and the NHL and wanted to make a project centered around hockey! This was originally made to serve as a helper for fantasy hockey, giving in depth stats, trends, etc. to find hidden gems in the league but as of right now, it is just a simple stat tracker. 

## Limitations
The API listed above does not allow for many calls back-to-back, so there are some safeguards to avoid response code 429 errors. The number of calls can be reduced but would require a bit of an overhaul

## How does it work
In the repository is the current up to date database (as of October 31,2026) so work with that can be accessed using sql however you see fit, but to update the db yourself, just run the file by doing "python main.py" in the terminal.