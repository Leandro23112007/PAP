@echo off

:: Executar como Administrador
net session >nul 2>&1 || (echo Por favor, execute este ficheiro como Administrador! & pause & exit)

:: Instalar cURL (se não estiver instalado)
winget install --id=cURL.cURL

:: Baixar e instalar Python
curl -o python-installer.exe https://www.python.org/ftp/python/3.14.0/python-3.14.0a1-amd64.exe
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

:: Verificar instalação do Python
python --version || (echo Erro na instalação do Python & pause & exit)

:: Atualizar pip
python.exe -m pip install --upgrade pip

:: Baixar e instalar MariaDB
curl -o mariadb-installer.msi https://mirrors.ptisp.pt/mariadb///mariadb-10.6.20/winx64-packages/mariadb-10.6.20-winx64.msi
start /wait msiexec /i mariadb-installer.msi /qn /norestart

:: Verificar instalação do MariaDB
mysql --version || (echo Erro na instalação do MariaDB & pause & exit)

:: Definir caminho do ficheiro CSV
set "DIR=%~dp0"
set "CaminhoProdutos=%DIR%produtos.csv"
echo %CaminhoProdutos%

:: Criar base de dados e tabelas
echo CREATE DATABASE IF NOT EXISTS loja; > create_database.sql
echo USE loja; > create_tables.sql
echo CREATE TABLE IF NOT EXISTS historico_precos_venda (ID INT AUTO_INCREMENT PRIMARY KEY, codigo_produto VARCHAR(50), nome_produto VARCHAR(255), preco_venda DECIMAL(10,2), data_venda DATE, preco_compra DECIMAL(10,2), data_compra DATE); >> create_tables.sql
echo CREATE TABLE IF NOT EXISTS inventario (ID INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), preco_venda VARCHAR(50), codigo VARCHAR(255), quantidade INT, preco_compra DECIMAL(10,2), ultima_adicao DATETIME, vendas INT, data_venda VARCHAR(50)); >> create_tables.sql
echo CREATE TABLE IF NOT EXISTS produtos (ID INT(11) AUTO_INCREMENT PRIMARY KEY, product_name VARCHAR(255), product_preco VARCHAR(50), product_estado VARCHAR(50), data_adicao TIMESTAMP, url VARCHAR(2048), nome_produto VARCHAR(255)); >> create_tables.sql

:: Criar base de dados e importar CSV
mysql -u root --password=leandro < create_database.sql
mysql -u root --password=leandro < create_tables.sql
mysql -u root --password=leandro loja < "%CaminhoProdutos%"

:: Instalar dependências Python
pip install mysql-connector-python
pip install csv os datetime timedelta decimal

:: Criar atalho no ambiente de trabalho
powershell "$WshShell = New-Object -ComObject WScript.Shell; $shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'GDS-Gestor de stocks.lnk')); $shortcut.TargetPath = '%DIR%pap\GDS-Gestor de stocks.py'; $shortcut.IconLocation = '%DIR%logo.ico'; $shortcut.Save()"

:: Iniciar o programa
cls
start python "%DIR%pap\GDS-Gestor de stocks.py"
echo Setup concluído!
pause
