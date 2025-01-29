@echo off
winget install --id=cURL.cURL

curl -o python-installer.exe https://www.python.org/ftp/python/3.11.4/python-3.11.4.exe

python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

curl -o mariadb-installer.msi https://downloads.mariadb.org/f/mariadb-10.6.9/winx64/mariadb-10.6.9-winx64.msi

msiexec /i mariadb-installer.msi /quiet /norestart

set "DIR=%~dp0"

set "CaminhoProdutos=%DIR%produtos.csv"

echo %CaminhoProdutos%


echo CREATE DATABASE IF NOT EXISTS loja; > create_database.sql


echo USE loja; > create_tables.sql
echo CREATE TABLE IF NOT EXISTS historico_precos_venda (ID INT AUTO_INCREMENT PRIMARY KEY, codigo_produto INT, nome_produto VARCHAR(255), preco_venda DECIMAL(10,2), data_venda DATE, preco_compra DECIMAL(10,2), data_compra DATE); >> create_tables.sql
echo CREATE TABLE IF NOT EXISTS inventario (ID INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), preco_venda VARCHAR(50), codigo INT, quantidade INT, preco_compra DECIMAL(10,2), ultima_adicao DATETIME, vendas INT, data_venda VARCHAR(50)); >> create_tables.sql
echo CREATE TABLE IF NOT EXISTS produtos (ID INT(11) AUTO_INCREMENT PRIMARY KEY, product_name VARCHAR(255), product_preco VARCHAR(50), product_estado VARCHAR(50), data_adicao TIMESTAMP, url VARCHAR(2048), nome_produto VARCHAR(255)); >> create_tables.sql


mysql -u root --password=leandro < create_database.sql
mysql -u root --password=leandro < create_tables.sql

mysql -u root --password=leandro a < "%CaminhoProdutos%"

pip install mysql-connector-python
pip install csv
pip install os
pip install datetime
pip install timedelta
pip install decimal

powershell "$WshShell = New-Object -ComObject WScript.Shell; $shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'GDS-Gestor de stocks.lnk')); $shortcut.TargetPath = '%DIR%pap\GDS-Gestor de stocks.py'; $shortcut.Save()"

cls

echo Setup concluido!

pause
