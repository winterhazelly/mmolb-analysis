echo "Player|Position|ERA|IP|AB|BA|OBP|SLG|PA|OPS||Team\n" > full_league.csv

curl -s "https://mmolb.com/api/league/6805db0cac48194de3cd3fee" > league.json

teams=($(jq ".Teams" league.json | tr -d '[],"'))

for line in ${teams[@]}
do
    python3 stats_riley.py $line
done

python3 stats_riley.py