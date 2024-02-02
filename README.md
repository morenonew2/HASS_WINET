## WINET-HA

Installazione 
Prerequisiti: 
-	HACS
  
I pkg seguenti vanno installati tramite HACS
-	Browser_mod
-	Card-mod
-	Layout-card
- Paper buttons row
- Hui-element
-	Scheduler-card
-	Scheduler (integrazione)
  
Il file configuration.yaml si trova nella cartella di configurazione di Homeassistant

che, in una tipica installazione standard, si trova in:

**˂config˃ = /home/homeassistant/.homeassistant/ (p.es.  installazione tipica su Raspberry)**

Configuration.yaml

Aggiungere testo evidenziato:

```
homeassistant:
  packages: !include_dir_named packages
.....................
lovelace:
  mode: storage
  dashboards:
    lovelace-winet:
      mode: yaml
      title: WINET
      icon: mdi:fire
      show_in_sidebar: true
      filename: winet_dashboard.yaml
    lovelace-x3relay:
      mode: yaml
      title: WINET X3
      icon: mdi:electric-switch
      show_in_sidebar: true
      filename: winet_x3relay_dashboard.yaml   
```
 


### Nella cartella ˂config˃ creare  file 
winet_dashboard.yaml:
```
title: WINET
views:
  - !include lovelace/winet_view.yaml
```

winet_x3relay_dashboard.yaml:
```
title: WINET X3
views:
  - !include lovelace/winet_x3relay_view.yaml
```
 
### Package
Nella cartella lovelace  (crearla in ˂config˃se non esiste)

Copiare file winet_view.yaml

Copiare file winet_x3relay_view.yaml

Nella cartella packages (crearla in ˂config˃se non esiste)

Copiare file winet_pkg.yaml

Copiare file winet_x3relay_pkg.yaml

### Immagini
Copiare in ˂config˃

la cartella www/Pictures/
 
### Risorse
Impostazioni > Plance > Risorse

Aggiungere 

URL: https://fonts.googleapis.com/css?family=Oswald

Tipo risorsa: foglio di stile

 
