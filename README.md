# Despliegue Seguro de MiniWebApp

Este repositorio contiene la configuración y los scripts necesarios para empaquetar, desplegar y monitorizar una aplicación web de ejemplo utilizando Docker, AWS EC2, Prometheus, Node Exporter y Grafana.

---

## Índice

1. [Primera Parte: Docker y HTTPS](#primera-parte-docker-y-https)  
2. [Segunda Parte: Despliegue en AWS EC2](#segunda-parte-despliegue-en-aws-ec2)  
3. [Tercera Parte: Prometheus y Node Exporter](#tercera-parte-prometheus-y-node-exporter)  
4. [Cuarta Parte: Integración con Grafana (opcional)](#cuarta-parte-integración-con-grafana-opcional)  

---

## Primera Parte: Docker y HTTPS

### 1. Configuración SSL del sitio web

- **Archivo de Virtual Host**:  
  - Ubicado en `apache/webapp.conf` (se copia luego a `/etc/apache2/sites-available/webapp.conf` dentro del contenedor).  
  - Define los bloques `<VirtualHost *:80>` y `<VirtualHost *:443>` con redirección HTTP→HTTPS y rutas a la aplicación WSGI.

- **Certificados**:  
  - Generados con OpenSSL y montados en `apache/certs/apache-selfsigned.{crt,key}`.  
  - El Dockerfile de Apache copia estos certificados y habilita el módulo SSL.

### 2. Empaquetado con Docker

- **Estructura de carpetas**  
[![image-1.png](https://i.postimg.cc/zfjqYjdd/image-1.png)](https://postimg.cc/bGs7QQfb)

  *Diagrama de la estructura del proyecto en disco, con los directorios `apache/`, `mysql/`, `webapp/` y el `docker-compose.yml` raíz.*

- **`apache/Dockerfile`**  
Construye un contenedor basado en Ubuntu, instala Apache+SSL, copia la configuración y los certificados, expone 80 y 443.

- **`mysql/Dockerfile`**  
Utiliza la imagen oficial de MySQL, añade el script de inicialización en `/docker-entrypoint-initdb.d/`, expone el puerto 3306.

- **`webapp/Dockerfile`**  
Basado en Python 3.11-slim, instala dependencias Flask y MySQL, expone el puerto 5000 y lanza la aplicación.

- **`docker-compose.yml`**  
Orquesta tres servicios:
1. **db**: MySQL con healthcheck y volumen persistente.
2. **flask**: tu aplicación, que depende de `db`.
3. **apache**: proxy HTTPS hacia Flask, que depende de `flask`.

---

## Segunda Parte: Despliegue en AWS EC2

1. **Preparación de la instancia**  
 - Inicia una instancia EC2 (Ubuntu 22.04), abre puertos 80 y 443 en el Security Group.
 - Instala Docker y Docker Compose.


 - En la EC2:  

    **Crear dokcer-compose.yaml** 

    ```YAML
    services:
      db:
        image: edwingd18/db:v1
        environment:
          MYSQL_ROOT_PASSWORD: example_root_pw
          MYSQL_DATABASE: mydb
          MYSQL_USER: user
          MYSQL_PASSWORD: secret
        volumes:
          - db_data:/var/lib/mysql
        healthcheck:
          test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "user", "-psecret"]
          interval: 5s
          timeout: 3s
          retries: 5

      flask:
        image: edwingd18/flask:v1
        depends_on:
          db:
            condition: service_healthy
        restart: on-failure
        environment:
          FLASK_ENV: production
          MYSQL_HOST: db
          MYSQL_USER: user
          MYSQL_PASSWORD: secret
          MYSQL_DATABASE: mydb
          MYSQL_PORT: 3306
        ports:
          - "5000:5000"

      apache:
        image: edwingd18/apache:v1
        depends_on:
          - flask
        ports:
          - "80:80"
          - "443:443"
    volumes:
      db_data:
    ```
    **Correr el docker compose**
    ```bash
   docker login
   # Crea un docker-compose.yml idéntico, apuntando a tus imágenes en Docker Hub
   docker compose up -d
   ```
2. **Verificación**  
 - Accede desde tu navegador a `http(s)://<IP-pública>` y comprueba que la app responde correctamente.

---

## Tercera Parte: Prometheus y Node Exporter

### 1. Instalación de Prometheus

- **Sistema de ficheros y usuario**  
- Crea el usuario `prometheus` y carpetas en `/etc/prometheus` y `/var/lib/prometheus`.
- **Binaries**  
- Descarga la release oficial, copia `prometheus` y `promtool` a `/usr/local/bin/`.
- Copia las carpetas `consoles` y `console_libraries` a `/etc/prometheus/`.
- **Servicio systemd**  
- Archivo `/etc/systemd/system/prometheus.service` con el comando de arranque apuntando a `/etc/prometheus/prometheus.yml`.
- **Configuración**  
- `prometheus.yml` habilita dos jobs:  
  - `prometheus` (auto-scrape en `127.0.0.1:9090`)  
  - `node_exporter` (scrape en `127.0.0.1:9100`)

### 2. Instalación de Node Exporter

- Descarga y copia el binario a `/usr/local/bin/node_exporter`.
- Crea `/etc/systemd/system/node_exporter.service`.
- Arranca y habilita el servicio con `systemctl enable --now node_exporter`.
- Verifica en `http://<IP-pública>:9090/targets` que ambos jobs estén “UP”.

### 3. Métricas de ejemplo

- **Memoria disponible**: `node_memory_MemAvailable_bytes`  
  [![Memoria disponible en Prometheus](https://i.postimg.cc/tJrbn40F/Screenshot-2025-05-26-232326.png)](https://postimg.cc/K3gwdF8Y)  
  *Gráfica que muestra la cantidad de memoria RAM libre en bytes a lo largo del tiempo. Útil para detectar fugas de memoria o picos de uso inesperados.*

- **Uso de CPU (idle)**: `rate(node_cpu_seconds_total{mode="idle"}[5m])`  
  [![Tasa de CPU idle](https://i.postimg.cc/NfzYgFkc/image.png)](https://postimg.cc/qzyWwkFb)  
  *Visualización de la tasa media de CPU inactiva durante ventanas de 5 minutos. Cuanto más alto, más ociosa está la CPU.*

- **Espacio en disco**: `node_filesystem_avail_bytes{fstype!="tmpfs"}`  
  [![Espacio libre en disco](https://i.postimg.cc/0QnRhyyh/image.png)](https://postimg.cc/FdYBLmcx)  
  *Evolución del espacio libre (en bytes) en las particiones reales del sistema (`ext4`, `xfs`, etc.), excluyendo `tmpfs`.*


---

## Cuarta Parte: Integración con Grafana (opcional)

1. **Instalación**:  
 - Instala Grafana en la misma máquina (o en un contenedor Docker).
2. **Fuente de datos**:  
 - Añade Prometheus como data source apuntando a `http://localhost:9090`.
## Cuarta Parte: Integración con Grafana (opcional)

- **Dashboard combinado**  
  [![Dashboard Grafana](https://i.postimg.cc/kXpVknVV/image.png)](https://postimg.cc/7fSYzrnD)  
  *Panel de Grafana con varias métricas: uso de CPU, memoria y disco. Permite tener una visión unificada del estado del servidor.*

- **Node Exporter Full**  
  [![Node Exporter Full](https://i.postimg.cc/x1mdhLD7/image.png)](https://postimg.cc/mPbRFzrN)  
  *Ejemplo de dashboard de la biblioteca oficial de Grafana para Node Exporter, mostrando un conjunto amplio de métricas del sistema.*

- **Prometheus 2.0 Overview**  
  [![Prometheus Overview](https://i.postimg.cc/yxW1PZyL/image.png)](https://postimg.cc/K3Shc4VT)  
  *Dashboard preconfigurado que muestra la salud de Prometheus, tiempos de scrape, uso de TSDB y otros indicadores de rendimiento del propio Prometheus.*
---

> ❗ **Nota**: Para detalles de comandos y configuraciones específicas, consulta los archivos correspondientes en cada carpeta (`apache/`, `mysql/`, `webapp/`) y los ficheros de servicio en `/etc/systemd/system/`.

---
