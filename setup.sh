
echo 'Installing python VENV \n'
sudo apt install python3.9-venv

echo 'creating virtual environment(s) \n'
python3 -m venv ./venv-notebook
python3 -m venv ./venv-dashboard

echo 'Activating environment and installing required modules \n'
. ./venv-notebook/bin/activate

pip install -r ./notebook_reqs.txt

. ./venv-dashboard/bin/activate

pip install -r ./dashboard_reqs.txt
