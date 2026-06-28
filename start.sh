if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/patelboss/Rashmibot1.git /Rashmibot
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /Rashmibot
fi
cd /Rashmibot
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
