# export all found in .env

export $(grep -v '^#' .env | xargs)