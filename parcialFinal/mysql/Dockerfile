# Utiliza la imagen oficial de MySQL
FROM mysql:latest

# Copia el script de inicialización al contenedor
COPY init.sql /docker-entrypoint-initdb.d/

# Expone el puerto por defecto de MySQL
EXPOSE 3306
