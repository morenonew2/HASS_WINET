## WINET-HA

Installazione 
Prerequisiti: 
-	HACS
  
I pkg seguenti vanno installati tramite HACS
-	Browser_mode
-	Card_mod
-	Layout-card
-	Scheduler-card
-	Scheduler (integrazione)
  
Il file configuration.yaml si trova nella cartella di configurazione di Homeassistant ˂config˃

**˂config˃ = /home/homeassistant/.homeassistant/ (p.es.  installazione tipica su Raspberry)**

Configuration.yaml
Aggiungere testo evidenziato:

```
homeassistant:
  packages: !include_dir_named packages
.......
lovelace:
  mode: storage
  dashboards:
    lovelace-winet:
      mode: yaml
      title: WINET
      icon: mdi:flower
      show_in_sidebar: true
      filename: winet_dashboard.yaml
    lovelace-X3Relay:
      mode: yaml
      title: X3Relay
      icon: mdi:flower
      show_in_sidebar: true
      filename: winet_dashboard.yaml
```
 


### Nella cartella ˂config˃ creare  file 
winet_dashboard.yaml:

```
title: WINET
views:
  - !include lovelace/winet_view.yaml
  - !include lovelace/winet_x3relay_view.yaml
```
 
### Package
Nella cartella lovelace  (crearla in ˂config˃se non esiste)
Copiare file winet_view.yaml 
Copiare file winet_x3relay_view.yaml

Nella cartella packages (crearla in ˂config˃se non esiste)
Copiare file winet_pkg.yaml
 
### Risorse
Impostazioni > Plance > Risorse

Aggiungere 

URL: https://fonts.googleapis.com/css?family=Oswald

Tipo risorsa: foglio di stile

 
