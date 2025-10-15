jekyll: RUBYOPT="--yjit" bundle exec jekyll build --watch --incremental
puma: bundle exec puma -p 4000 -t 0:5 -e development -b tcp://127.0.0.1:4000
# open: sleep 3 && open http://localhost:4000