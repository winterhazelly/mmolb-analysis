echo "Player|Position|ERA|IP|AB|BA|OBP|SLG|PA|OPS||Team" > full_league.csv

leagueID=6805db0cac48194de3cd3fee

curl -s "https://mmolb.com/api/league/"$leagueID > league.json

teams=($(jq ".Teams" league.json | tr -d '[],"'))

for line in ${teams[@]}
do
    python3 stats_riley.py $line
done
