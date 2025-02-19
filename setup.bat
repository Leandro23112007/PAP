@echo off

:: Executar como Administrador
net session >nul 2>&1 || (echo Por favor, execute este ficheiro como Administrador! & pause & exit)

:: Instalar cURL (se não estiver instalado)
winget install --id=cURL.cURL

:: Baixar e instalar Python (usando versão estável)
curl -o "%~dp0python-installer.exe" https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe
start /wait "%~dp0python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1

:: Verificar instalação do Python
python --version || ( start %~dp0python-installer.exe)
echo Erro na instalação:Instalar Python manualmente & pause

:: Atualizar pip
python -m pip install --upgrade pip

:: Baixar e instalar MariaDB
winget install -e --id MariaDB.Server

:: Verificar instalação do MariaDB

mariadb --version || ( echo Erro na instalação:Instalar Python manualmente & pause & start %~dp0mariadb-installer.msi )


:: Definir caminho do ficheiro CSV
set "DIR=%~dp0"
set "CaminhoProdutos=%DIR%Recursos\produtos.csv"
echo %CaminhoProdutos%x

del %DIR%python-installer.exe
del %DIR%mariadb-installer.msi

:: Criar base de dados e tabelas
echo CREATE DATABASE IF NOT EXISTS loja; > create_database.sql
echo USE loja; > create_tables.sql
echo CREATE TABLE IF NOT EXISTS historico_precos_venda (ID INT AUTO_INCREMENT PRIMARY KEY, codigo_produto VARCHAR(50), nome_produto VARCHAR(255), preco_venda DECIMAL(10,2), data_venda DATE, preco_compra DECIMAL(10,2), data_compra DATE); >> create_tables.sql
echo CREATE TABLE IF NOT EXISTS inventario (ID INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), preco_venda VARCHAR(50), codigo VARCHAR(255), quantidade INT, preco_compra DECIMAL(10,2), ultima_adicao DATETIME, vendas INT, data_venda VARCHAR(50)); >> create_tables.sql
echo CREATE TABLE IF NOT EXISTS produtos (ID INT(11) AUTO_INCREMENT PRIMARY KEY, product_name VARCHAR(255), product_preco VARCHAR(50), product_estado VARCHAR(50), data_adicao TIMESTAMP, url VARCHAR(2048), nome_produto VARCHAR(255)); >> create_tables.sql

:: Criar base de dados e importar CSV

echo Escolher uma palavra-passe para o MariaDB:
set /p password=
mariadb -u root --password=%password% < create_database.sql
mariadb -u root --password=%password% < create_tables.sql
mariadb -u root --password=%password% loja < "%CaminhoProdutos%"

:: Instalar dependências Python
pip install mysql-connector-python

:: Criar atalho no ambiente de trabalho
powershell "$WshShell = New-Object -ComObject WScript.Shell; $shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'GDS-Gestor de stocks.lnk')); $shortcut.TargetPath = '%DIR%pap\GDS-Gestor de stocks.py'; $shortcut.IconLocation = '%DIR%Recursos\logo.ico'; $shortcut.Save()"

:: Iniciar o programa
cls
echo Setup concluído! & pause
start python "%DIR%pap\GDS-Gestor de stocks.py"