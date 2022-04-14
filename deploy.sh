printf "\033[1;31mStarting\033[0m\n"
docker-compose build --no-cache && docker-compose up -d --force-recreate